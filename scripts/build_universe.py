#!/usr/bin/env python3
"""
Builds the master stock universe and the part index the daily data job runs on.

Every screener list (nasdaq100, sp500, growth, value, dividend, international,
and later the whole US market) is membership only: tickers and curated names.
This script unions them, removes duplicates, and assigns each ticker to a
numbered part of at most PART_SIZE stocks, then writes data/stocks/index.json.
The daily job fetches one part per matrix leg, so a stock held by four lists is
fetched once a day instead of four times (measured 2026-09-28: 932 fetches a
day for 629 unique tickers, a third of them redundant).

Parts are ordered by importance, so the screener's default view stays one
download: part 1 leads with the Nasdaq 100, then the rest of the S&P 500, then
Growth, Value and Dividend, then International. LIST_PRIORITY sets that order.

A ticker keeps its part for as long as it stays in any list, so parts do not
reshuffle daily and each part file's git history stays a clean per-stock series
(v4.4.0's score-history sparklines mine exactly that). A ticker that leaves
every list frees its slot, which the next new ticker reuses.

Because stickiness can eventually place a new list member in a later part, the
index does NOT assume a list occupies a fixed part range: it records the parts
each list actually spans, so the frontend fetches what the index says rather
than what the priority order implies.

Deliberately NOT in the universe: data/etfs.json. ETF records share only 7 of
their 20 fields with stock records, come from fetch_etf_data.py, and score on a
different model, so screener_etfs.json stays its own feed (see PRD, v4.9.0).

Two files, split by who reads them. index.json is the frontend bootstrap and
is deliberately tiny (about 1 KB, and it does not grow with the universe): the
parts that exist, and which parts each list spans. tickers.json is the full
ticker-to-part map for per-ticker consumers (Automate Fundamentals asking which
part holds MSFT) and for this pipeline's own --part mode; it scales with the
universe, which is why it is not in the file every page load fetches.

Names are not duplicated into either file. They live in the list files, which
is what "lists are membership only" means, and the fetcher reads them from
there through name_map() below.

Single writer by design: only this script writes these two files, so the
parallel part jobs never contend over them. Each part file carries its own
`updated` stamp, which is where per-part freshness lives.

Run by constituents.yml after the list syncs, and safe to run by hand:
  python scripts/build_universe.py            (writes if the mapping changed)
  python scripts/build_universe.py --check    (exits 1 if it WOULD change)
"""

import argparse
import datetime
import json
import os
import sys

PART_SIZE = 500
INDEX_PATH = "data/stocks/index.json"
TICKERS_PATH = "data/stocks/tickers.json"
PARTS_DIR = "data/stocks"

# Order matters: it decides which part a ticker lands in, and therefore how
# many files the screener downloads for each view. Highest-traffic list first.
# `vti` is listed now but its file does not exist until v4.9.3; missing lists
# are skipped, so adding the file is the only step needed to switch it on.
LIST_PRIORITY = [
    ("nasdaq100", "data/nasdaq100.json"),
    ("sp500", "data/sp500.json"),
    ("growth", "data/vug.json"),
    ("value", "data/vtv.json"),
    ("dividend", "data/vig.json"),
    ("intl", "data/vxus.json"),
    ("vti", "data/vti.json"),
]


def load_list(path):
    """Return [(ticker, name), ...] from a constituent list file."""
    with open(path, encoding="utf-8") as f:
        rows = json.load(f)
    out = []
    for r in rows:
        if isinstance(r, dict):
            t = str(r.get("t") or "").strip()
            n = str(r.get("n") or "").strip() or t
        else:
            t = str(r).strip()
            n = t
        if t:
            out.append((t, n))
    return out


def name_map():
    """Return {ticker: curated name}, highest-priority list winning.

    The fetcher uses this instead of a `names` block in index.json, so the
    list files stay the single source of truth for display names.
    """
    names = {}
    for _, path in LIST_PRIORITY:
        if not os.path.exists(path):
            continue
        for t, n in load_list(path):
            names.setdefault(t, n)
    return names


def part_map():
    """Return {ticker: part number} from tickers.json."""
    with open(TICKERS_PATH, encoding="utf-8") as f:
        return json.load(f)["tickers"]


def build():
    """Return (index_dict, stats). Pure: reads lists and the old index only."""
    lists = {}
    order = []          # tickers in priority order, first appearance wins
    names = {}
    for key, path in LIST_PRIORITY:
        if not os.path.exists(path):
            continue
        rows = load_list(path)
        lists[key] = {"list": path, "tickers": [t for t, _ in rows]}
        for t, n in rows:
            if t not in names:
                names[t] = n          # curated name from the highest-priority list
                order.append(t)
    if not order:
        sys.exit("ABORT: no constituent lists found; refusing to write an empty universe.")

    # --- sticky part assignment ---
    old = {}
    try:
        old = part_map()
    except Exception:
        old = {}

    current = set(order)
    assigned = {}
    counts = {}
    for t in order:
        p = old.get(t)
        # Honor an existing assignment only if that part still has room for it.
        if isinstance(p, int) and p >= 1 and counts.get(p, 0) < PART_SIZE:
            assigned[t] = p
            counts[p] = counts.get(p, 0) + 1

    # Place the rest (new tickers, and any displaced by a full part) in the
    # lowest-numbered part with room, keeping priority order so part 1 fills
    # with the most important names first on a cold build.
    for t in order:
        if t in assigned:
            continue
        p = 1
        while counts.get(p, 0) >= PART_SIZE:
            p += 1
        assigned[t] = p
        counts[p] = counts.get(p, 0) + 1

    n_parts = max(assigned.values())
    parts = [{"file": f"part-{p:02d}.json", "count": counts.get(p, 0)}
             for p in range(1, n_parts + 1)]

    for key, info in lists.items():
        spans = sorted({assigned[t] for t in info["tickers"] if t in assigned})
        info["parts"] = spans
        info["count"] = len(info["tickers"])

    now = (datetime.datetime.now(datetime.timezone.utc)
           .isoformat().replace("+00:00", "Z"))
    index = {
        "updated": now,
        "partSize": PART_SIZE,
        "parts": parts,
        # Membership arrays stay out: they are already in the list files, and
        # carrying them here would put ~70 KB in the frontend's first request
        # once the whole market lands.
        "lists": {k: {"list": lists[k]["list"],
                      "parts": lists[k]["parts"],
                      "count": lists[k]["count"]}
                  for k, _ in LIST_PRIORITY if k in lists},
    }
    tickers = {"updated": now, "tickers": {t: assigned[t] for t in order}}
    stats = {
        "unique": len(order),
        "parts": n_parts,
        "slots": sum(len(v["tickers"]) for v in lists.values()),
        "reused": sum(1 for t in order if old.get(t) == assigned[t]),
        "moved": sorted(t for t in order if t in old and old[t] != assigned[t]),
        "added": sorted(t for t in order if t not in old),
        "dropped": sorted(t for t in old if t not in current),
    }
    return index, tickers, stats


def main():
    ap = argparse.ArgumentParser(description="Build the master universe part index.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the mapping would change; write nothing")
    args = ap.parse_args()

    index, tickers, st = build()

    def read(path):
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    # `updated` always differs, so compare only the parts that matter.
    def shape(d, keys):
        return {k: d.get(k) for k in keys} if d else None

    prev_index, prev_tickers = read(INDEX_PATH), read(TICKERS_PATH)
    changed = (shape(prev_index, ("partSize", "parts", "lists")) !=
               shape(index, ("partSize", "parts", "lists"))
               or shape(prev_tickers, ("tickers",)) != shape(tickers, ("tickers",)))

    print(f"[universe] {st['unique']} unique tickers from {st['slots']} list slots "
          f"({st['slots'] - st['unique']} duplicates removed), {st['parts']} parts.")
    for p in index["parts"]:
        print(f"           {p['file']}: {p['count']}")
    for key, info in index["lists"].items():
        print(f"           {key:10s} {info['count']:5d} tickers, parts {info['parts']}")
    if st["added"]:
        print(f"[universe] added: {st['added'][:20]}{' ...' if len(st['added']) > 20 else ''}")
    if st["dropped"]:
        print(f"[universe] dropped: {st['dropped'][:20]}{' ...' if len(st['dropped']) > 20 else ''}")
    if st["moved"]:
        print(f"[universe] moved part: {st['moved'][:20]}{' ...' if len(st['moved']) > 20 else ''}")

    if args.check:
        print("[universe] index is up to date." if not changed
              else "[universe] index WOULD change.")
        return 1 if changed else 0

    if not changed:
        print("[universe] no change; index.json and tickers.json left alone.")
        return 0

    os.makedirs(PARTS_DIR, exist_ok=True)
    for path, payload in ((INDEX_PATH, index), (TICKERS_PATH, tickers)):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)
            f.write("\n")
        print(f"[universe] wrote {path}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
