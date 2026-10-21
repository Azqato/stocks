#!/usr/bin/env python3
"""
Builds data/earnings_calendar.json for the Invests Earnings Calendar (v5.12.0):
every stock's next earnings report, in one small file, so the page doesn't load
the stock parts.

Reads the earnDate fields fetch_screener_data.py stores on each stock (from
the same Yahoo quote, no extra requests) and keeps reports from a week ago
onward: Yahoo keeps the last report's date until the next is announced, and a
date that old is stale rather than upcoming.

Output:
  { "updated": ISO, "source": "yahoo",
    "reports": [ {"t", "n", "d", "e"?, "time"?, "est"?}, ... ] }   sorted by date
  d     YYYY-MM-DD, US Eastern
  e     last day of an unconfirmed multi-day window (only when present)
  time  "bmo" before the open / "amc" after the close (only when known)
  est   true when the date is Yahoo's estimate (only when true)

Usage: build_earnings_calendar.py [FEED ...] [--out PATH]
  FEEDs default to data/stocks/part-*.json; any {stocks: {...}} feed works,
  which is how a single list is tested locally.
"""

import argparse
import datetime
import glob
import json
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
KEEP_DAYS = 7  # keep reports this many days back


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("feeds", nargs="*")
    ap.add_argument("--out", default="data/earnings_calendar.json")
    args = ap.parse_args()
    feeds = args.feeds or sorted(glob.glob("data/stocks/part-*.json"))

    cutoff = (datetime.datetime.now(ET).date() - datetime.timedelta(days=KEEP_DAYS)).isoformat()
    reports, seen = [], set()
    for path in feeds:
        with open(path, encoding="utf-8") as f:
            stocks = json.load(f)["stocks"]
        for t, s in stocks.items():
            d = s.get("earnDate")
            if t in seen or not d or d < cutoff:
                continue
            seen.add(t)
            r = {"t": t, "n": s.get("name") or t, "d": d}
            if s.get("earnDateEnd"):
                r["e"] = s["earnDateEnd"]
            if s.get("earnTime"):
                r["time"] = s["earnTime"]
            if s.get("earnEst"):
                r["est"] = True
            reports.append(r)
    reports.sort(key=lambda r: (r["d"], r["t"]))

    out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "source": "yahoo", "reports": reports}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
        f.write("\n")
    print(f"{len(reports)} upcoming reports from {len(feeds)} feed(s) -> {args.out}")


if __name__ == "__main__":
    main()
