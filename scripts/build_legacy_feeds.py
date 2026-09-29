#!/usr/bin/env python3
"""
Derives the per-list screener feeds from the master universe part files.

From v4.9.0 the daily job fetches parts, not lists, so nothing writes
data/screener*.json any more. This script regroups records already fetched into
exactly the feeds the site and Automate Fundamentals read today, with no extra
Yahoo calls. Schemas, filenames and field order are unchanged, which is the
whole point: the frontend stays untouched until v4.9.1, and v4.4.0's score
history keeps mining the same files' git diffs without a schema break.

Feeds written (see FEEDS): screener.json, screener_sp500.json, screener_intl.json
as { updated, source, stocks }, and screener_gvd.json as { updated, source,
universes: { growth|value|dividend: { updated, source, stocks } } }.

A stock's `name` comes from the list being written, not from the part file,
because each list keeps its own curated name for the same ticker (the old
per-list runs did the same in build_stocks).

Runs after every part in a day's matrix has landed, since a single list can
span several parts (sp500 spans parts 1 and 2 today). Missing tickers are
reported and skipped rather than fabricated: a feed is allowed to be short if a
part job failed, and MIN_COVERAGE decides when short becomes an abort.

  python scripts/build_legacy_feeds.py
  python scripts/build_legacy_feeds.py --parts-only 1   (recompute from part 1)
"""

import argparse
import datetime
import json
import os
import sys

import build_universe

PARTS_DIR = build_universe.PARTS_DIR
INDEX_PATH = build_universe.INDEX_PATH

# Feeds, each naming the lists it carries. A single-list feed is flat; a
# multi-list feed is nested under `universes`, keyed as screener.js expects.
FEEDS = [
    ("data/screener.json", [("nasdaq100", None)]),
    ("data/screener_sp500.json", [("sp500", None)]),
    ("data/screener_gvd.json", [("growth", "growth"), ("value", "value"),
                                ("dividend", "dividend")]),
    ("data/screener_intl.json", [("intl", None)]),
]

# A feed missing more than this fraction of its list means a part job failed
# badly enough that overwriting a good feed with a gutted one is worse than
# failing loudly. Individual symbols Yahoo has no data for are not missing
# here: they are present with null metrics, which score zero by design.
MIN_COVERAGE = 0.90


def load_parts():
    """Return (index, {ticker: record}, {part number: that part's stamp})."""
    with open(INDEX_PATH, encoding="utf-8") as f:
        index = json.load(f)
    records, stamps = {}, {}
    for n, p in enumerate(index["parts"], start=1):
        path = os.path.join(PARTS_DIR, p["file"])
        if not os.path.exists(path):
            print(f"[legacy] WARNING: {path} missing; feeds will be short.",
                  file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as f:
            body = json.load(f)
        records.update(body["stocks"])
        stamps[n] = body.get("updated")
    if not records:
        sys.exit("ABORT: no part files found; run fetch_screener_data.py --part N first.")
    return index, records, stamps


def stocks_for(list_path, records, missing):
    """Return {ticker: record} for one list, in that list's own order."""
    out = {}
    for ticker, name in build_universe.load_list(list_path):
        rec = records.get(ticker)
        if rec is None:
            missing.append(ticker)
            continue
        rec = dict(rec)
        rec["name"] = name          # each list keeps its own curated name
        out[ticker] = rec
    return out


def main():
    ap = argparse.ArgumentParser(description="Derive the per-list feeds from the parts.")
    ap.add_argument("--dry-run", action="store_true",
                    help="report what each feed would contain; write nothing")
    args = ap.parse_args()

    index, records, stamps = load_parts()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    failures = []

    def as_of(spans):
        """The oldest stamp among the parts a list spans, or now if unknown.

        The stamp has to describe the DATA, not this script's run time. Stamping
        every derived feed `now` would report a feed as fresh even when the part
        job that feeds it failed hours ago, which is precisely the case the
        screener's stale banner exists to catch. screener.js does the same thing
        for the whole-market universe (oldest contributing part wins), so both
        paths report freshness the same way.
        """
        have = [stamps[p] for p in spans if stamps.get(p)]
        return min(have) if have else now

    for out_path, members in FEEDS:
        blocks = {}
        counts = []
        for list_key, feed_key in members:
            info = index["lists"].get(list_key)
            if info is None:
                print(f"[legacy] skipping {list_key}: not in the universe index.")
                continue
            missing = []
            stocks = stocks_for(info["list"], records, missing)
            expected = info["count"]
            if expected and len(stocks) < expected * MIN_COVERAGE:
                failures.append(f"{list_key}: {len(stocks)}/{expected} records")
            if missing:
                print(f"[legacy] {list_key}: {len(missing)} tickers absent from the "
                      f"parts: {missing[:10]}{' ...' if len(missing) > 10 else ''}")
            blocks[feed_key or list_key] = {
                "updated": as_of(info["parts"]), "source": "yahoo",
                "stocks": stocks}
            counts.append(f"{list_key} {len(stocks)}/{expected}")

        if not blocks:
            continue
        if len(members) == 1:
            body = next(iter(blocks.values()))
            out = {"updated": body["updated"], "source": "yahoo",
                   "stocks": body["stocks"]}
        else:
            out = {"updated": min(b["updated"] for b in blocks.values()),
                   "source": "yahoo", "universes": blocks}

        if args.dry_run:
            print(f"[legacy] would write {out_path}: {'; '.join(counts)}")
            continue
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
        print(f"[legacy] wrote {out_path}: {'; '.join(counts)}")

    if failures:
        sys.exit("ABORT: coverage below "
                 f"{MIN_COVERAGE:.0%}, refusing to publish gutted feeds: "
                 + "; ".join(failures))
    return 0


if __name__ == "__main__":
    sys.exit(main())
