#!/usr/bin/env python3
"""
Rates an ETF's top-10 holdings with the site's individual-stock scoring model.

Ad hoc, run by hand, not on a cron and not wired into any feed. Answers the
question "what would the screener say about the companies inside these funds?"
for arbitrary tickers the owner supplies, including funds that are not in
data/etfs.json.

This is deliberately NOT the ETF universe model in screener.js (ETF_METRICS:
technicals and long-horizon returns). That model grades a fund as a timing
decision. This script ignores the wrapper entirely, including expense ratio,
yield, and every technical, and grades only the underlying companies on
fundamentals, then rolls them up by fund weight.

Scoring is relative, the same way the live screener is. By default a holding is
ranked against the committed daily feed for its market: domestic holdings
against the S&P 500 (`data/screener_sp500.json`), foreign-listed holdings
against the International feed (`data/screener_intl.json`). Each pool is ranked
independently, exactly as the site ranks within whichever universe is loaded, so
a holding that is in a feed scores what the site shows for it. Holdings missing
from a feed (a second share class, a fund-only name) are fetched and added to
that pool.

`--universe holdings` restores the original self-contained behavior, ranking the
holdings only against each other. That is useful for comparing funds head to
head but produces much harsher, less stable tiers: with only a few dozen
mega-caps in the pool and no weak companies to sit below them, strong companies
are forced into the bottom bands, and the tiers shift whenever the fund list
changes. Prefer an index baseline when quoting a rating.

fetch() and num() are imported from fetch_screener_data rather than copied, so
the metric definitions here cannot drift from the live daily pipeline. The
scoring curve, weights, and tier cuts below are a hand port of screener.js
(METRICS, pointsFromPct, computeScoreMap, computeTierMap) and DO have to be
kept in sync by hand if that file's model changes.

Usage:
  python scripts/analyze_etf_holdings.py SCHD SCHG SCHB
  python scripts/analyze_etf_holdings.py SCHD SCHG --out report.md
  python scripts/analyze_etf_holdings.py SCHD --json raw.json

Env:
  PAUSE   seconds to wait between symbols (default 0.8), honored by fetch_screener_data
"""

import argparse
import json
import sys
import time

import yfinance as yf

from fetch_screener_data import PAUSE, fetch, num

# Yahoo's fund-holdings endpoint returns a handful of foreign listings under an
# exchange suffix its own quote endpoint then rejects. Map them to the symbol
# that actually resolves. Keyed by what top_holdings returns.
SYMBOL_FIXES = {
    "005930.KQ": "005930.KS",  # Samsung Electronics: KOSDAQ suffix returned, KOSPI is correct
    "000660.KQ": "000660.KS",  # SK hynix: same, and .KQ silently returns a different instrument's price
    "RY": "RY.TO",             # Royal Bank of Canada: the intl feed tracks the Toronto listing
}

# A holding scoring on fewer than this many of the six metrics is treated as
# unfetched rather than rated. Without this, a bad symbol that still returns a
# price (see SYMBOL_FIXES) scores near-zero on five hard zeros and renders as a
# confident F, which is indistinguishable from a genuinely weak company.
MIN_METRICS = 3

# Committed daily feeds usable as a ranking baseline, by shorthand name. A raw
# path works too. These are the same files the live screener loads, so scoring
# against one reproduces what the site shows for a holding that is in it.
UNIVERSE_FEEDS = {
    "sp500": "data/screener_sp500.json",
    "nasdaq100": "data/screener.json",
    "intl": "data/screener_intl.json",
    "growth": "data/screener_gvd.json",
    "value": "data/screener_gvd.json",
    "dividend": "data/screener_gvd.json",
}

# Hand port of screener.js METRICS (stock universes). Weights total 100.
# The two weight-0 context metrics in screener.js (peVsG, netCashMc) are
# omitted: they color cells in the UI and contribute nothing to the score.
CLAMP_Q = 0.22
METRIC_WEIGHTS = [
    ("revTTM", 10, True),
    ("revFwd", 10, True),
    ("epsTTM", 15, True),
    ("epsFwd", 15, True),
    ("pegFwd", 25, False),
    ("cashDebt", 25, True),
]
TIER_CUTS = [("s", 0.10), ("a", 0.20), ("b", 0.50), ("c", 0.75)]  # f = the rest
TIER_LABELS = {"sp": "S+", "s": "S", "a": "A", "b": "B", "c": "C", "f": "F"}

# Absolute bands for the fund-level weighted average. These are a presentation
# convenience for a single roll-up number and are NOT the site's tier model:
# site tiers are a rank within a universe, so they cannot be applied to an
# average that is not itself a member of that universe.
RATING_BANDS = [(80, "Excellent"), (60, "Above Average"), (45, "Average"), (30, "Below Average")]


def metric_value(key, d):
    """One metric's raw comparable value for a holding, or None if unscorable."""
    if key == "pegFwd":
        pe = d.get("peFwd")
        if pe is not None and pe <= 0:
            return float("inf")  # unprofitable: Yahoo's PEG is unreliable, rank worst
        peg = d.get("pegFwd")
        return peg if (peg is not None and peg > 0) else None
    if key == "cashDebt":
        cash, debt = d.get("cash"), d.get("debt")
        if cash is None or debt is None:
            return None
        if debt == 0:
            return float("inf") if cash > 0 else None
        return cash / debt
    return num(d.get(key))


def points_from_pct(p):
    v = 20 * (p - CLAMP_Q) / (1 - 2 * CLAMP_Q)
    return max(0.0, min(20.0, v))


def compute_scores(data):
    """Percentile-rank every holding on every metric and sum to a 0-100 score.

    Holdings with too little data are dropped from the ranking pools entirely,
    not just from the final score: leaving them in would let a bad symbol's
    stray value shift everyone else's percentile on that metric.
    """
    coverage = {t: sum(1 for key, _, _ in METRIC_WEIGHTS if metric_value(key, data[t]) is not None)
                for t in data}
    thin = sorted(t for t in data if coverage[t] < MIN_METRICS)
    tickers = [t for t in data if coverage[t] >= MIN_METRICS]
    pts = {t: {} for t in tickers}
    total_weight = sum(w for _, w, _ in METRIC_WEIGHTS)

    for key, _weight, higher in METRIC_WEIGHTS:
        vals = []
        for t in tickers:
            v = metric_value(key, data[t])
            if v is not None:
                vals.append((v, t))
        n = len(vals)
        if not n:
            continue
        vals.sort(key=lambda x: x[0])
        i = 0
        while i < n:
            j = i
            while j + 1 < n and vals[j + 1][0] == vals[i][0]:
                j += 1  # average-rank ties
            perc = ((i + j) / 2) / (n - 1) if n > 1 else 0.5
            if not higher:
                perc = 1 - perc
            p = points_from_pct(perc)
            for k in range(i, j + 1):
                pts[vals[k][1]][key] = p
            i = j + 1

    scores = {}
    for t in tickers:
        total = 0.0
        have = 0
        for key, weight, _ in METRIC_WEIGHTS:
            p = pts[t].get(key)
            if p is None:
                continue  # missing = hard zero, the denominator stays at 100
            have += 1
            total += p * (weight / 20)
        scores[t] = round(total / total_weight * 100) if have else None
    for t in thin:
        scores[t] = None
        print(f"WARN {t}: only {coverage[t]}/{len(METRIC_WEIGHTS)} metrics available, not rated",
              file=sys.stderr)
    return scores, pts, thin


def compute_tiers(scores):
    """Rank-based tier bands, ties rounding up into the better band."""
    order = sorted([t for t in scores if scores[t] is not None],
                   key=lambda t: scores[t], reverse=True)
    n = len(order)
    if not n:
        return {}
    cuts = [max(1, round(q * n)) for _, q in TIER_CUTS]
    for k in range(len(cuts)):
        j = min(cuts[k], n) - 1
        boundary = scores[order[j]]
        while j + 1 < n and scores[order[j + 1]] == boundary:
            j += 1
        cuts[k] = j + 1
        if k > 0 and cuts[k] < cuts[k - 1]:
            cuts[k] = cuts[k - 1]

    tiers = {}
    ci = 0
    for i, t in enumerate(order):
        while ci < len(cuts) and i >= cuts[ci]:
            ci += 1
        tiers[t] = "sp" if scores[t] >= 100 else (TIER_CUTS[ci][0] if ci < len(TIER_CUTS) else "f")
    return tiers


def load_universe(spec):
    """Load a screener feed as {symbol: record} to rank holdings against."""
    path = UNIVERSE_FEEDS.get(spec, spec)
    with open(path, encoding="utf-8") as f:
        feed = json.load(f)
    if "universes" in feed:
        if spec in feed["universes"]:
            return dict(feed["universes"][spec]["stocks"]), f"{spec} ({path})"
        merged = {}
        for sub in feed["universes"].values():
            merged.update(sub["stocks"])
        return merged, f"all universes in {path}"
    return dict(feed.get("stocks", {})), path


def match_symbol(sym, universe):
    """Find a holding in a feed, allowing for the dot/dash dual-class spelling split."""
    for cand in (sym, sym.replace("-", "."), sym.replace(".", "-")):
        if cand in universe:
            return cand
    return None


# A trailing exchange suffix (".TW", ".KS", ".L") means a foreign listing. The
# domestic dual-class spellings are the exception: those dots are share classes.
DOMESTIC_DOT_SUFFIXES = {"A", "B", "C"}


def is_foreign(sym):
    if "." not in sym:
        return False
    return sym.rsplit(".", 1)[1].upper() not in DOMESTIC_DOT_SUFFIXES


def get_holdings(etf):
    """Top holdings for one fund as [{symbol, name, weight}], weight a fraction."""
    df = yf.Ticker(etf).funds_data.top_holdings
    out = []
    for sym, row in df.iterrows():
        out.append({
            "symbol": str(sym),
            "name": str(row.get("Name", "")),
            "weight": num(row.get("Holding Percent")) or 0.0,
        })
    return out


def rating_for(score):
    for floor, label in RATING_BANDS:
        if score >= floor:
            return label
    return "Weak"


def render(etfs, holdings, scores, tiers, pool_of, basis):
    lines = []
    lines.append("# ETF top-holdings analysis")
    lines.append("")
    lines.append(basis)
    lines.append("")
    lines.append("Technicals, expense ratio, and dividend yield are excluded: this rates "
                 "the underlying companies only.")
    lines.append("")

    summary = []
    for etf in etfs:
        hl = holdings.get(etf) or []
        lines.append(f"## {etf}")
        lines.append("")
        if not hl:
            lines.append("No holdings returned.")
            lines.append("")
            continue
        lines.append("| Ticker | Company | Weight | Score | Tier | Ranked in |")
        lines.append("|---|---|---|---|---|---|")
        wsum = 0.0
        acc = 0.0
        for h in sorted(hl, key=lambda x: (scores.get(x["symbol"]) is None,
                                           -(scores.get(x["symbol"]) or 0))):
            sym = h["symbol"]
            s = scores.get(sym)
            tier = TIER_LABELS.get(tiers.get(sym), "n/a")
            shown = "n/a" if s is None else str(s)
            lines.append(f"| {sym} | {h['name']} | {h['weight'] * 100:.2f}% | {shown} | "
                         f"{tier} | {pool_of.get(sym, 'n/a')} |")
            if s is not None:
                acc += s * h["weight"]
                wsum += h["weight"]
        avg = acc / wsum if wsum else None
        unrated = [h["symbol"] for h in hl if scores.get(h["symbol"]) is None]
        lines.append("")
        if avg is None:
            lines.append("**Overall: no scorable holdings.**")
        else:
            rated = len(hl) - len(unrated)
            detail = f"from {rated} of {len(hl)} holdings"
            if unrated:
                detail += f", excluding {', '.join(unrated)} for insufficient data"
            lines.append(f"**{etf} overall: weighted avg {avg:.1f}, {rating_for(avg)}** ({detail}).")
            summary.append((etf, avg))
        lines.append("")

    if summary:
        lines.append("## Summary")
        lines.append("")
        lines.append("| ETF | Weighted Avg | Rating |")
        lines.append("|---|---|---|")
        for etf, avg in sorted(summary, key=lambda x: -x[1]):
            lines.append(f"| {etf} | {avg:.1f} | {rating_for(avg)} |")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(
        description="Rate ETF top-10 holdings with the site's individual-stock model.")
    ap.add_argument("etfs", nargs="+", help="ETF tickers, e.g. SCHD SCHG FNDX")
    ap.add_argument("--out", help="write the markdown report here (default: stdout)")
    ap.add_argument("--json", dest="json_path", help="also write raw holdings/fundamentals/scores here")
    ap.add_argument("--universe", default="sp500",
                    help="feed to rank domestic holdings against (shorthand or path, "
                         "default sp500); 'holdings' ranks them against each other instead")
    ap.add_argument("--intl-universe", dest="intl_universe", default="intl",
                    help="feed to rank foreign-listed holdings against (default intl); "
                         "'holdings' folds them into the domestic pool")
    args = ap.parse_args()

    etfs = [e.upper() for e in args.etfs]

    holdings = {}
    for etf in etfs:
        try:
            holdings[etf] = get_holdings(etf)
            got = len(holdings[etf])
            note = "" if got == 10 else f"  (returned {got}, not 10)"
            print(f"{etf}: {got} holdings{note}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001 - one bad fund must not kill the run
            print(f"{etf}: holdings failed: {e!r}", file=sys.stderr)
            holdings[etf] = []
        time.sleep(PAUSE)

    symbols = []
    for hl in holdings.values():
        for h in hl:
            if h["symbol"] not in symbols:
                symbols.append(h["symbol"])

    # Each pool is ranked independently, the way the live screener ranks within
    # whichever universe is loaded. A holding already in a feed reuses that
    # feed's own record, so its score matches what the site shows; anything
    # missing (a second share class, a fund-only name) is fetched and added.
    pools = {}
    labels = {}
    for name, spec in (("domestic", args.universe), ("international", args.intl_universe)):
        if spec == "holdings":
            continue
        pools[name], labels[name] = load_universe(spec)

    data = {}
    pool_of = {}
    key_for = {}
    for sym in symbols:
        canon = SYMBOL_FIXES.get(sym, sym)
        target = "international" if (is_foreign(canon) and "international" in pools) else "domestic"
        if target not in pools:
            pools.setdefault("domestic", {})
            labels.setdefault("domestic", "the holdings themselves")
            target = "domestic"
        hit = match_symbol(canon, pools[target])
        if hit:
            key_for[sym] = hit
        else:
            try:
                pools[target][canon] = fetch(canon)
            except Exception as e:  # noqa: BLE001 - score what resolved, report what did not
                print(f"{sym}: fetch failed: {e!r}", file=sys.stderr)
                pools[target][canon] = {}
            key_for[sym] = canon
            time.sleep(PAUSE)
        pool_of[sym] = target
        data[sym] = pools[target][key_for[sym]]

    scores = {}
    tiers = {}
    pts = {}
    thin = []
    sizes = {}
    for name, pool in pools.items():
        s, p, t = compute_scores(pool)
        ti = compute_tiers(s)
        sizes[name] = len(pool)
        thin += t
        # Re-key from pool symbols back to the holding symbols the tables use.
        for sym in symbols:
            if pool_of.get(sym) == name:
                scores[sym] = s.get(key_for[sym])
                tiers[sym] = ti.get(key_for[sym])
                pts[sym] = p.get(key_for[sym], {})

    basis = "; ".join(f"**{name}** holdings ranked in `{labels[name]}` ({sizes[name]} companies)"
                      for name in sorted(pools) if sizes.get(name))
    report = render(etfs, holdings, scores, tiers, pool_of, "Scored against " + basis + ".")
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report + "\n")
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(report)

    if args.json_path:
        with open(args.json_path, "w", encoding="utf-8") as f:
            json.dump({"holdings": holdings, "fundamentals": data, "scores": scores,
                       "tiers": tiers, "points": pts, "unrated": thin,
                       "pool_of": pool_of, "pool_key": key_for,
                       "pool_sizes": sizes}, f, indent=2)
            f.write("\n")
        print(f"Wrote {args.json_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
