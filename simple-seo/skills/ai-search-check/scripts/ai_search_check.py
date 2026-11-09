#!/usr/bin/env python3
"""AI Search Check for the simple-seo plugin.

Reads one web page and its site's robots.txt, then prints a JSON summary:
which AI and search crawlers may reach the page, what is in the page's HTML,
and what structured data it has. It only reads. It identifies itself honestly.

Usage: python3 ai_search_check.py URL
Works with Python 3.9 or later and uses curl to fetch.
"""

import html
import json
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

USER_AGENT = "Mozilla/5.0 (compatible; AISearchCheck/1.0; simple-seo plugin)"
MAX_BYTES = 5_000_000
ROBOTS_MAX_BYTES = 500 * 1024  # Google reads only the first 500 KiB of robots.txt

# Crawler tokens, checked against each company's own documentation in November 2026.
# (token, company, job, token whose rules it follows when robots.txt doesn't name it)
CRAWLERS = [
    ("Googlebot", "Google", "search", None),          # Google Search, including AI Overviews and AI Mode
    ("Bingbot", "Microsoft", "search", None),         # Bing, which also feeds Copilot
    ("OAI-SearchBot", "OpenAI", "search", None),      # ChatGPT search
    ("Claude-SearchBot", "Anthropic", "search", None),
    ("PerplexityBot", "Perplexity", "search", None),
    ("Applebot", "Apple", "search", "googlebot"),     # Siri, Spotlight and Safari. Apple follows Googlebot's rules if Applebot isn't named
    ("DuckAssistBot", "DuckDuckGo", "search", None),  # DuckDuckGo's AI answers
    ("Meta-WebIndexer", "Meta", "search", None),      # Meta AI's search
    ("ChatGPT-User", "OpenAI", "user", None),         # Fetches a page when a ChatGPT user asks
    ("Claude-User", "Anthropic", "user", None),
    ("Perplexity-User", "Perplexity", "user", None),
    ("Meta-ExternalFetcher", "Meta", "user", None),
    ("GPTBot", "OpenAI", "training", None),
    ("ClaudeBot", "Anthropic", "training", None),
    ("Google-Extended", "Google", "training", None),  # Gemini training and Gemini apps' answers. Doesn't affect Google Search
    ("Applebot-Extended", "Apple", "training", None),
    ("Meta-ExternalAgent", "Meta", "training", None),
    ("CCBot", "Common Crawl", "training", None),
]


# ---------- Fetching ----------

def decode(data, headers):
    """Use the charset from the headers, or from a <meta charset> near the top of the page."""
    m = re.search(r"charset=[\"']?([\w-]+)", headers.get("content-type", ""), re.I)
    name = m.group(1) if m else None
    if not name:
        m = re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", data[:2048], re.I)
        name = m.group(1).decode("ascii", "ignore") if m else "utf-8"
    try:
        return data.decode(name, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


def fetch(url):
    """Fetch with curl. Returns status, final URL, final headers (lower-case keys), body text."""
    with tempfile.TemporaryDirectory() as tmp:
        head, body = Path(tmp, "h"), Path(tmp, "b")
        cmd = ["curl", "-sS", "-L", "--compressed", "--max-redirs", "10", "--max-time", "25",
               "--max-filesize", str(MAX_BYTES), "-A", USER_AGENT,
               "-D", str(head), "-o", str(body), "-w", "%{http_code} %{url_effective}", url]
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
        except (OSError, subprocess.TimeoutExpired) as e:
            return {"ok": False, "error": str(e)}
        if out.returncode != 0:
            return {"ok": False, "error": (out.stderr or "curl failed").strip()}
        code, _, final = out.stdout.strip().partition(" ")
        raw_head = head.read_text(errors="replace") if head.exists() else ""
        blocks = [b for b in re.split(r"\r?\n\r?\n", raw_head) if b.strip()]
        headers = {}
        if blocks:
            for line in blocks[-1].splitlines()[1:]:
                k, sep, v = line.partition(":")
                if sep:
                    key = k.strip().lower()
                    headers[key] = (headers[key] + ", " if key in headers else "") + v.strip()
        data = body.read_bytes() if body.exists() else b""
        return {"ok": True, "status": int(code or 0), "final_url": final, "headers": headers,
                "redirects": max(0, len(blocks) - 1), "bytes": data, "text": decode(data, headers)}


# ---------- robots.txt (RFC 9309) ----------

def parse_robots(text):
    """Returns a list of groups: {"agents": [lower-case tokens], "rules": [(allow, pattern)]}."""
    text = text.lstrip("﻿")
    groups, current, last_was_agent = [], None, False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        field, value = (s.strip() for s in line.split(":", 1))
        field = field.lower()
        if field == "user-agent":
            if not last_was_agent:
                current = {"agents": [], "rules": []}
                groups.append(current)
            current["agents"].append(value.split("/")[0].strip().lower())
            last_was_agent = True
        elif field in ("allow", "disallow"):
            last_was_agent = False
            if current is None:
                continue  # Rules before any User-agent line belong to no group
            if value == "" and field == "disallow":
                continue  # An empty Disallow allows everything
            current["rules"].append((field == "allow", value))
        # Other lines, like Sitemap and Crawl-delay, don't change the groups
    return groups


def rules_for(groups, token, fallback=None):
    for name in (token.lower(), fallback):
        if not name:
            continue
        named = [g for g in groups if name in g["agents"]]
        if named:
            return [r for g in named for r in g["rules"]], name
    star = [g for g in groups if "*" in g["agents"]]
    return [r for g in star for r in g["rules"]], ("*" if star else None)


def pattern_matches(pattern, path):
    pattern = unquote(pattern)
    if not pattern.startswith(("/", "*")):
        return False  # Google ignores rules that don't start with / or *
    regex = re.escape(pattern).replace(r"\*", ".*")
    if regex.endswith(r"\$"):
        regex = regex[:-2] + "$"
    return re.match(regex, unquote(path)) is not None


def is_allowed(rules, path):
    """Longest matching rule wins. On a tie, Allow wins."""
    if path.lower() == "/robots.txt":
        return True, None
    best = None
    for allow, pattern in rules:
        if pattern_matches(pattern, path):
            key = (len(pattern), allow)
            if best is None or key > best[0]:
                best = (key, allow, pattern)
    if best is None:
        return True, None
    return best[1], ("Allow: " if best[1] else "Disallow: ") + best[2]


def check_robots(page_url):
    parts = urlsplit(page_url)
    robots_url = urlunsplit((parts.scheme, parts.netloc, "/robots.txt", "", ""))
    path = (parts.path or "/") + ("?" + parts.query if parts.query else "")
    res = fetch(robots_url)
    result = {"url": robots_url}
    if not res["ok"]:
        result.update(status="unreachable", note="Couldn't fetch robots.txt: " + res["error"])
        return result, None
    if res["status"] in (401, 403):
        result.update(status=f"refused ({res['status']})",
                      note="The site refused to show robots.txt to this check. Real crawlers may get a different answer")
        return result, None
    if res["status"] >= 500 or res["status"] == 429:
        result.update(status=f"error ({res['status']})",
                      note="Crawlers may treat a robots.txt server error as 'stay away from the whole site'")
        return result, None
    if res["status"] >= 400:
        result.update(status=f"missing ({res['status']})", note="No robots.txt, so every crawler is allowed")
        groups = []
    else:
        result["status"] = "found"
        result["note"] = "Some sites show different robots.txt rules to different visitors"
        text = res["bytes"][:ROBOTS_MAX_BYTES].decode("utf-8", errors="replace")
        if "<html" in text[:1000].lower():
            result["note"] = "robots.txt returned a web page instead of rules, so it was read as empty"
            groups = []
        else:
            groups = parse_robots(text)
            result["sitemaps"] = re.findall(r"(?im)^\s*sitemap:\s*(\S+)", text)[:5]
            if len(res["bytes"]) > ROBOTS_MAX_BYTES:
                result["note"] = "robots.txt is larger than 500 KiB. Only the first 500 KiB was read, as Google does"
    crawlers = []
    for token, company, job, fallback in CRAWLERS:
        rules, group = rules_for(groups, token, fallback)
        page_ok, page_rule = is_allowed(rules, path)
        home_ok, _ = is_allowed(rules, "/")
        crawlers.append({"token": token, "company": company, "job": job,
                         "page_allowed": page_ok, "home_allowed": home_ok,
                         "matched_group": group, "deciding_rule": page_rule})
    result["named_groups"] = sorted({a for g in groups for a in g["agents"] if a != "*"})[:40]
    return result, crawlers


# ---------- Page HTML ----------

SKIP_TEXT = {"script", "style", "noscript", "template", "svg", "head"}
APP_ROOTS = ("root", "app", "__next", "__nuxt", "svelte", "___gatsby")
VOID = {"meta", "link", "img", "br", "hr", "input", "source", "area", "base", "col", "embed", "wbr", "track", "param"}
QUESTION = re.compile(r"^(how|what|why|when|where|who|which|can|does|do|is|are|should|will)\b", re.I)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.skip, self.in_head, self.svg = [], 0, False, 0
        self.title, self.title_done, self.in_title = "", False, False
        self.meta, self.links, self.times, self.lang = [], [], [], None
        self.headings, self.cur_heading = [], None
        self.text_all, self.text_main, self.main_depth = [], [], 0
        self.after_h1, self.seen_h1 = [], False
        self.jsonld, self.cur_jsonld = [], None
        self.root_depth, self.root_seen, self.root_text = 0, False, []
        self.counts = {"script": 0, "table": 0, "ul": 0, "ol": 0, "itemscope": 0, "rdfa": 0, "img_no_alt": 0}

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang")
        if "itemscope" in a:
            self.counts["itemscope"] += 1
        if "typeof" in a:
            self.counts["rdfa"] += 1
        if tag in self.counts:
            self.counts[tag] += 1
        if tag == "img" and "alt" not in a:
            self.counts["img_no_alt"] += 1
        if tag == "body" and self.in_head:  # A missing </head> shouldn't hide the whole page
            self.in_head = False
            self.skip = max(0, self.skip - 1)
        if tag == "head":
            self.in_head = True
        if tag == "svg":
            self.svg += 1
        if tag == "meta":
            self.meta.append(a)
        elif tag == "link":
            self.links.append(a)
        elif tag == "time":
            self.times.append(a.get("datetime", ""))
        elif tag == "title" and not self.svg and not self.title_done:
            self.in_title = True
        elif tag == "script" and "ld+json" in a.get("type", "").lower():
            self.cur_jsonld = []
        if tag in ("h1", "h2", "h3"):
            self.cur_heading = [tag, []]
        if tag in ("main", "article") or a.get("role") == "main":
            self.main_depth += 1
        if tag == "div" and a.get("id") in APP_ROOTS and not self.root_seen:
            self.root_seen, self.root_depth = True, 1
        elif self.root_depth and tag not in VOID:
            self.root_depth += 1
        if tag in SKIP_TEXT:
            self.skip += 1
        if tag not in VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == "title" and self.in_title:
            self.in_title, self.title_done = False, True
        if tag == "head":
            self.in_head = False
        if tag == "svg" and self.svg:
            self.svg -= 1
        if tag == "script" and self.cur_jsonld is not None:
            self.jsonld.append("".join(self.cur_jsonld))
            self.cur_jsonld = None
        if self.cur_heading and tag == self.cur_heading[0]:
            text = " ".join(" ".join(self.cur_heading[1]).split())
            self.headings.append((tag, text))
            if tag == "h1":
                self.seen_h1 = True
            self.cur_heading = None
        if tag in ("main", "article") and self.main_depth:
            self.main_depth -= 1
        if self.root_depth and tag not in VOID:
            self.root_depth -= 1
        if tag in SKIP_TEXT and self.skip:
            self.skip -= 1
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass

    def handle_data(self, data):
        if self.cur_jsonld is not None:
            self.cur_jsonld.append(data)
            return
        if self.in_title:
            self.title += data
        if self.skip:
            return
        if self.cur_heading:
            self.cur_heading[1].append(data)
        self.text_all.append(data)
        if self.main_depth:
            self.text_main.append(data)
        if self.root_depth:
            self.root_text.append(data)
        if self.seen_h1 and not (self.cur_heading and self.cur_heading[0] == "h1"):
            self.after_h1.append(data)


def words(chunks):
    joined = " ".join(" ".join(chunks).split())
    return joined.split(" ") if joined else []


# Small helper types inside structured data that don't describe the page itself
MINOR_TYPES = {"PostalAddress", "GeoCoordinates", "Offer", "AggregateOffer", "ImageObject", "ListItem",
               "OpeningHoursSpecification", "Rating", "AggregateRating", "ContactPoint", "SearchAction",
               "EntryPoint", "PropertyValue", "QuantitativeValue", "MonetaryAmount", "Brand",
               "Person", "Review", "ReadAction", "SiteNavigationElement", "VideoObject", "Place",
               "DefinedRegion", "City", "State", "Country", "AdministrativeArea", "WebPageElement",
               "PriceSpecification", "UnitPriceSpecification", "ShippingDeliveryTime", "OfferShippingDetails",
               "MerchantReturnPolicy", "Thing", "Question", "Answer", "HowToStep",
               "HowToSection", "Comment", "ItemList"}
PAGE_TYPES = {"WebSite", "WebPage", "BreadcrumbList", "CollectionPage", "ItemPage", "AboutPage", "ContactPage", "FAQPage", "SearchResultsPage"}


def schema_items(node, out, depth=0):
    if depth > 12:
        return
    if isinstance(node, list):
        for n in node:
            schema_items(n, out, depth + 1)
    elif isinstance(node, dict):
        if "@type" in node:
            types = node["@type"] if isinstance(node["@type"], list) else [node["@type"]]
            if depth == 0 or not all(str(t) in MINOR_TYPES for t in types):
                out.append(node)
        for key, value in node.items():
            if isinstance(value, (dict, list)):
                schema_items(value, out, depth + 1)


def describe_schema(blocks):
    found, errors, seen = [], [], set()
    for i, raw in enumerate(blocks):
        try:
            data = json.loads(raw)
        except ValueError:
            try:
                data = json.loads(raw, strict=False)
                errors.append(f"Block {i + 1} has line breaks inside its text. Most tools accept it, but it isn't strict JSON")
            except ValueError as e:
                errors.append(f"Block {i + 1} is not valid JSON: {e}")
                continue
        items = []
        schema_items(data, items)
        for it in items:
            types = [str(t) for t in (it["@type"] if isinstance(it["@type"], list) else [it["@type"]])]
            if all(t in MINOR_TYPES for t in types):
                continue
            entry = {"type": types, "fields": sorted(k for k in it if not k.startswith("@"))[:30]}
            for key in ("name", "telephone", "url", "priceRange", "dateModified", "datePublished", "headline"):
                if isinstance(it.get(key), (str, int, float)):
                    entry[key] = html.unescape(str(it[key]))[:120]
            addr = it.get("address")
            if isinstance(addr, list) and addr:
                addr = addr[0]
            if isinstance(addr, dict):
                entry["address"] = ", ".join(html.unescape(str(addr.get(k, ""))) for k in
                                             ("streetAddress", "addressLocality", "addressRegion", "postalCode")
                                             if addr.get(k))
            elif isinstance(addr, str):
                entry["address"] = addr[:160]
            key = json.dumps(entry, sort_keys=True)
            if key not in seen:
                seen.add(key)
                found.append(entry)
    return found, errors


def matches_page(entry, visible):
    """Does each key fact in the structured data also appear in the page's visible text?"""
    low, digits = visible.lower(), re.sub(r"\D", "", visible)
    out = {}
    if entry.get("name"):
        out["name"] = entry["name"].lower() in low
    if entry.get("telephone"):
        phone = re.sub(r"\D", "", entry["telephone"])[-10:]
        out["telephone"] = bool(phone) and phone in digits
    if entry.get("address"):
        street = entry["address"].split(",")[0].strip().lower()
        out["address"] = bool(street) and street in low
    return out


DIRECTIVE_NAMES = {"max-snippet", "max-image-preview", "max-video-preview", "unavailable_after",
                   "ai-grounding", "ai-training"}


def parse_directives(value, default_bot):
    """Splits 'noindex, bingbot: noarchive' into [(bot, directive)]. bot is None for everyone."""
    out, bot = [], default_bot
    for part in value.split(","):
        part = part.strip().lower()
        m = re.match(r"^([a-z0-9_-]+)\s*:\s*(.+)$", part)
        if m and m.group(1) not in DIRECTIVE_NAMES:
            bot, part = m.group(1), m.group(2).strip()
        if part:
            out.append((bot, part))
    return out


def directives_summary(pairs):
    def has(name, bots=(None, "googlebot")):
        return any(b in bots and (d == name or d.startswith(name + ":")) for b, d in pairs)

    def value(name, bots):
        for b, d in pairs:
            if b in bots and d.startswith(name):
                return d.split(":", 1)[1].strip() if ":" in d else None
        return None

    return {
        "noindex": has("noindex") or has("none"),
        "nosnippet": has("nosnippet"),
        "max_snippet": value("max-snippet", (None, "googlebot")),
        "bing_noindex": has("noindex", (None, "bingbot")) or has("none", (None, "bingbot")),
        "bing_noarchive": has("noarchive", (None, "bingbot")),
        "bing_nocache": has("nocache", (None, "bingbot")),
        "bing_ai_grounding": value("ai-grounding", (None, "bingbot")),
        "bing_ai_training": value("ai-training", (None, "bingbot")),
        "raw": [f"{b}: {d}" if b else d for b, d in pairs][:10],
    }


def check_page(url):
    res = fetch(url)
    if not res["ok"]:
        return {"status": "unreachable", "error": res["error"]}
    h = res["headers"]
    out = {"status": res["status"], "final_url": res["final_url"], "redirects": res["redirects"],
           "content_type": h.get("content-type", ""),
           "behind_cloudflare": "cloudflare" in h.get("server", "").lower() or "cf-ray" in h}
    if res["status"] in (401, 403, 405, 429, 503):
        out["blocked"] = "The site refused the check. It may block automated requests"
    p = PageParser()
    try:
        p.feed(res["text"])
        p.close()
    except Exception as e:  # Broken HTML shouldn't stop the whole check
        out["parse_warning"] = str(e)

    def meta(name=None, prop=None):
        for m in p.meta:
            if name and m.get("name", "").lower() == name:
                return m.get("content", "")
            if prop and m.get("property", "").lower() == prop:
                return m.get("content", "")
        return None

    meta_pairs = []
    for m in p.meta:
        n = m.get("name", "").lower()
        if n in ("robots", "googlebot", "bingbot"):
            meta_pairs += parse_directives(m.get("content", ""), None if n == "robots" else n)
    header_pairs = parse_directives(h["x-robots-tag"], None) if "x-robots-tag" in h else []
    canonical = next((l.get("href") for l in p.links if "canonical" in l.get("rel", "").lower().split()), None)
    all_words, main_words = words(p.text_all), words(p.text_main)
    schema, schema_errors = describe_schema(p.jsonld)
    visible = " ".join(all_words)
    for entry in schema:
        if entry.get("name") and not any(t in PAGE_TYPES for t in entry["type"]):
            entry["found_on_page"] = matches_page(entry, visible)
    excerpt_words = main_words if len(main_words) >= 100 else all_words
    h2h3 = [t for tag, t in p.headings if tag in ("h2", "h3")]
    almost_empty = len(all_words) < 50
    empty_app_root = p.root_seen and len(words(p.root_text)) < 20
    out.update({
        "title": " ".join(p.title.split()),
        "meta_description": meta(name="description"),
        "canonical": canonical,
        "lang": p.lang,
        "robots_meta": directives_summary(meta_pairs),
        "x_robots_tag": directives_summary(header_pairs) if header_pairs else None,
        "h1": [t for tag, t in p.headings if tag == "h1"],
        "h2_h3": h2h3[:25],
        "question_headings": sum(1 for t in h2h3 if t.endswith("?") or QUESTION.match(t)),
        "words_in_html": len(all_words),
        "words_in_main_content": len(main_words) if p.text_main else None,
        "first_150_words_after_h1": " ".join(words(p.after_h1)[:150]) or None,
        "main_content_excerpt": " ".join(excerpt_words[:400]) or None,
        "lists": p.counts["ul"] + p.counts["ol"],
        "tables": p.counts["table"],
        "scripts": p.counts["script"],
        "images_without_alt": p.counts["img_no_alt"],
        "almost_empty": almost_empty,
        "empty_app_root": empty_app_root,
        "likely_needs_javascript": almost_empty or (empty_app_root and len(main_words) < 150),
        "structured_data": schema,
        "structured_data_errors": schema_errors,
        "microdata_or_rdfa": p.counts["itemscope"] + p.counts["rdfa"] > 0,
        "dates": {
            "article_modified": meta(prop="article:modified_time"),
            "article_published": meta(prop="article:published_time"),
            "time_tags": [t for t in p.times if t][:5],
        },
    })
    return out


def main():
    if len(sys.argv) != 2 or not re.match(r"^https?://", sys.argv[1]):
        print(json.dumps({"error": "Give one full page address, starting with http:// or https://"}))
        sys.exit(2)
    url = sys.argv[1]
    page = check_page(url)
    robots, crawlers = check_robots(page.get("final_url") or url)
    print(json.dumps({"checked_url": url, "page": page, "robots_txt": robots,
                      "crawlers": crawlers}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
