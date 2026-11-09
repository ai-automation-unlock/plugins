# Quick Wins analysis for the simple-seo plugin.
# Runs inside Composio's remote workbench, where run_composio_tool() is built in.
# Set the four settings below, then run the whole file as one cell.

SITE = ""          # Search Console property, e.g. "https://www.example.com/" or "sc-domain:example.com". "" = pick automatically
ACCOUNT = ""       # Composio account ID or alias for Google Search Console. "" = the default account
BRAND_TERMS = []   # The business's name, e.g. ["acme plumbing"]. Searches containing it are left out
SKIP_DOMAIN = True # Also leave out searches containing the domain name. Set to False if that drops real service searches

import datetime, json, re
from urllib.parse import urlsplit

DAYS = 90             # Length of the date range
LAG_DAYS = 3          # Search Console data for the last few days is incomplete
MIN_IMPRESSIONS = 20  # A search term needs at least this many impressions in the range to count
MIN_BUCKET_CLICKS = 20        # Enough clicks to trust your site's own click rate for a position range
MIN_EXPECTED_CLICKS = 10      # Only call a click rate low when the site would normally expect this many clicks
TOP_N = 10
MAX_ROWS = 50000      # Stop fetching after this many rows, so very big sites finish in time

BUCKETS = [("1-3", 0, 3.5), ("4-10", 3.5, 10.5), ("11-20", 10.5, 20.5)]


def bucket_of(position):
    for name, low, high in BUCKETS:
        if low < position <= high:
            return name
    return None


def brand_stem(site):
    host = site.split("sc-domain:")[-1]
    host = (urlsplit(host).hostname or host).strip("/").lower()
    labels = host.split(".")
    if len(labels) >= 3 and labels[-2] in ("co", "com", "org", "net", "gov", "ac", "edu"):
        name = labels[-3]
    else:
        name = labels[-2] if len(labels) >= 2 else labels[0]
    return re.sub(r"[^a-z0-9]", "", name)


def is_brand(query, stems):
    squashed = re.sub(r"[^a-z0-9]", "", query.lower())
    return any(s and s in squashed for s in stems)


def address_key(u):
    p = urlsplit(u)
    host = (p.hostname or "").lower()
    if host.startswith("www."):
        host = host[4:]
    return host + p.path.rstrip("/") + ("?" + p.query if p.query else "")


def same_address(a, b):
    return address_key(a) == address_key(b)


def analyze(rows, site, brand_terms=(), skip_domain=True):
    """rows: Search Console rows with keys [page, query]. Returns the report as a dict."""
    stems = [re.sub(r"[^a-z0-9]", "", t.lower()) for t in brand_terms]
    domain = brand_stem(site)
    if skip_domain and len(domain) >= 4:
        stems.append(domain)
    clean, brand = [], {}
    for r in rows:
        page, query = r["keys"][0], r["keys"][1]
        if is_brand(query, stems):
            brand[query] = brand.get(query, 0) + r.get("impressions", 0)
            continue
        clean.append({"page": page, "query": query, "clicks": r.get("clicks", 0),
                      "impressions": r.get("impressions", 0), "position": r.get("position", 0.0)})

    # Your site's own click rate for each position range, weighted by impressions
    site_ctr = {}
    for name, low, high in BUCKETS:
        inside = [r for r in clean if low < r["position"] <= high]
        imp = sum(r["impressions"] for r in inside)
        clk = sum(r["clicks"] for r in inside)
        site_ctr[name] = {"impressions": imp, "clicks": clk,
                          "ctr": (clk / imp) if imp else None,
                          "trusted": clk >= MIN_BUCKET_CLICKS}

    def target_ctr(name):
        b = site_ctr[name]
        return b["ctr"] if b["trusted"] else None

    # Search terms where two different pages both show up
    by_query = {}
    for r in clean:
        if r["impressions"] >= MIN_IMPRESSIONS and r["position"] <= 20.5:
            by_query.setdefault(r["query"], []).append(r)
    competing = []
    for q, rs in by_query.items():
        pages = sorted({r["page"] for r in rs})
        if len(pages) > 1:
            groups = []
            for p in pages:
                for g in groups:
                    if same_address(g[0], p):
                        g.append(p)
                        break
                else:
                    groups.append([p])
            kind = "same page at two addresses" if len(groups) == 1 else "two pages compete"
            if len(groups) > 1 and any(len(g) > 1 for g in groups):
                kind += ", and one also shows at two addresses"
            competing.append({"query": q, "pages": pages, "kind": kind,
                              "impressions": sum(r["impressions"] for r in rs)})
    competing.sort(key=lambda c: -c["impressions"])

    # Treat one page that shows at two addresses (like with and without a final /) as one page
    page_imp = {}
    for r in clean:
        page_imp[r["page"]] = page_imp.get(r["page"], 0) + r["impressions"]
    rep, also_at, by_key = {}, {}, {}
    for p in sorted(page_imp, key=lambda p: -page_imp[p]):
        main_p = by_key.get(address_key(p))
        if main_p is None:
            by_key[address_key(p)] = p
            rep[p], also_at[p] = p, []
        else:
            rep[p] = main_p
            also_at[main_p].append(p)
    merged = {}
    for r in clean:
        key = (rep[r["page"]], r["query"])
        m = merged.setdefault(key, {"page": key[0], "query": key[1], "clicks": 0,
                                    "impressions": 0, "_pos": 0.0})
        m["clicks"] += r["clicks"]
        m["impressions"] += r["impressions"]
        m["_pos"] += r["position"] * r["impressions"]
    for m in merged.values():
        m["position"] = m.pop("_pos") / m["impressions"] if m["impressions"] else 0.0

    # Score each search term
    wins = []
    for r in merged.values():
        b = bucket_of(r["position"])
        if b is None or r["impressions"] < MIN_IMPRESSIONS:
            continue
        ctr = r["clicks"] / r["impressions"]
        own = target_ctr(b)
        weak_title = (own is not None and r["impressions"] * own >= MIN_EXPECTED_CLICKS
                      and ctr < 0.5 * own)
        if b == "1-3":
            if not weak_title:
                continue
            kind, goal = "top spot, few clicks", target_ctr("1-3")
        elif b == "4-10":
            kind, goal = "almost top 3", target_ctr("1-3")
        else:
            kind, goal = "page two", target_ctr("4-10")
        extra = None if goal is None else max(0.0, r["impressions"] * (goal - ctr))
        wins.append({**r, "ctr": ctr, "kind": kind, "weak_title": weak_title,
                     "extra_clicks_estimate": extra})

    # Group by page
    pages = {}
    for w in wins:
        pages.setdefault(w["page"], []).append(w)
    can_estimate = all(target_ctr(n) is not None for n in ("1-3", "4-10"))
    out = []
    for page, ws in pages.items():
        if can_estimate:
            ws.sort(key=lambda w: (-(w["extra_clicks_estimate"] or 0), -w["impressions"]))
            score = sum(w["extra_clicks_estimate"] or 0 for w in ws)
        else:
            ws.sort(key=lambda w: -w["impressions"])
            score = sum(w["impressions"] for w in ws)
        if score <= 0:
            continue
        main = ws[0]
        addresses = [page] + also_at.get(page, [])
        out.append({
            "page": page,
            "also_at": also_at.get(page, []),
            "main_query": main["query"],
            "kind": main["kind"],
            "weak_title": main["weak_title"],
            "impressions": main["impressions"],
            "clicks": main["clicks"],
            "ctr": round(main["ctr"], 4),
            "position": round(main["position"], 1),
            "extra_clicks_per_month_all_searches": None if not can_estimate else round(score * 30 / DAYS, 1),
            "other_queries": [{"query": w["query"], "impressions": w["impressions"],
                               "position": round(w["position"], 1)} for w in ws[1:4]],
            "competes": [c for c in competing if c["kind"] != "same page at two addresses"
                         and any(a in c["pages"] for a in addresses)][:2],
            "_score": score,
        })
    out.sort(key=lambda p: -p["_score"])
    for p in out:
        del p["_score"]

    return {
        "ranked_by": "estimated extra clicks" if can_estimate else "impressions (not enough top-3 data to estimate clicks)",
        "named_search_totals": {"clicks": sum(r.get("clicks", 0) for r in rows),
                                "impressions": sum(r.get("impressions", 0) for r in rows)},
        "site_ctr_by_position": {k: {"impressions": v["impressions"], "clicks": v["clicks"],
                                     "ctr": None if v["ctr"] is None else round(v["ctr"], 4),
                                     "trusted": v["trusted"]} for k, v in site_ctr.items()},
        "rows_used": len(clean),
        "brand_filter": stems,
        "brand_searches_left_out": len(brand),
        "top_brand_searches_left_out": sorted(brand, key=lambda q: -brand[q])[:10],
        "candidates_found": len(out),
        "candidates": out[:TOP_N],
        "competing": competing[:5],
    }


def _call(slug, args):
    result, error = run_composio_tool(slug, args, account=ACCOUNT or None)
    if error:
        raise RuntimeError(f"{slug} failed: {error}")
    if isinstance(result, dict) and result.get("successful") is False:
        raise RuntimeError(f"{slug} failed: {result.get('error')}")
    data = result.get("data", result)
    return data.get("response_data", data) if isinstance(data, dict) else data


def pick_site():
    data = _call("GOOGLE_SEARCH_CONSOLE_LIST_SITES", {})
    entries = data.get("siteEntry") or []
    usable = [e["siteUrl"] for e in entries if e.get("permissionLevel") != "siteUnverifiedUser"]
    return usable


def fetch_totals(site, start, end):
    try:
        data = _call("GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY", {
            "site_url": site, "start_date": start, "end_date": end,
            "dimensions": [], "search_type": "web", "row_limit": 1})
    except RuntimeError:
        return None
    rows = data.get("rows") or []
    if len(rows) != 1 or rows[0].get("keys"):
        return None  # Not a whole-site total
    return {"clicks": rows[0].get("clicks", 0), "impressions": rows[0].get("impressions", 0)}


def fetch_rows(site, start, end):
    rows, start_row = [], 0
    while True:
        data = _call("GOOGLE_SEARCH_CONSOLE_SEARCH_ANALYTICS_QUERY", {
            "site_url": site, "start_date": start, "end_date": end,
            "dimensions": ["page", "query"], "search_type": "web",
            "row_limit": 5000, "start_row": start_row})
        batch = data.get("rows") or []
        rows.extend(batch)
        if len(batch) < 5000:
            return rows, False
        if len(rows) >= MAX_ROWS:
            return rows, True
        start_row += 5000


def main():
    site = SITE
    if not site:
        sites = pick_site()
        if not sites:
            return {"status": "no_sites"}
        if len(sites) != 1:
            return {"status": "choose_site", "sites": sites}
        site = sites[0]
    end = datetime.date.today() - datetime.timedelta(days=LAG_DAYS)
    start = end - datetime.timedelta(days=DAYS - 1)
    rows, capped = fetch_rows(site, start.isoformat(), end.isoformat())
    if not rows:
        return {"status": "no_data", "site": site, "start": start.isoformat(), "end": end.isoformat()}
    report = analyze(rows, site, BRAND_TERMS, SKIP_DOMAIN)
    return {"status": "ok", "site": site, "start": start.isoformat(), "end": end.isoformat(),
            "site_totals": fetch_totals(site, start.isoformat(), end.isoformat()),
            "rows_fetched": len(rows), "rows_capped": capped, **report}


if __name__ == "__main__" and "run_composio_tool" in globals():
    print(json.dumps(main(), indent=1))
