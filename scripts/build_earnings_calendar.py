#!/usr/bin/env python3
"""
Builds data/earnings_calendar.json for the Invests Earnings Calendar (v5.12.0):
every stock's next earnings report, in one small file, so the page doesn't load
the stock parts.

Reads the earnDate fields fetch_screener_data.py stores on each stock (from
the same Yahoo quote, no extra requests) for US-dollar listings, and keeps reports from a week ago
onward: Yahoo keeps the last report's date until the next is announced, and a
date that old is stale rather than upcoming.

Output:
  { "updated": ISO, "source": "yahoo",
    "reports": [ {"t", "n", "d", "c"?, "e"?, "time"?, "est"?}, ... ],  sorted by date
    "fomc": [ {"start", "end", "sep"}, ... ] }
  d     YYYY-MM-DD, US Eastern
  e     last day of an unconfirmed multi-day window (only when present)
  time  "bmo" before the open / "amc" after the close (only when known)
  est   true when the date is Yahoo's estimate (only when true)
  c     market cap in $ millions, so the page can list the biggest first
  fomc  the Fed's scheduled FOMC meetings (v5.12.1), read from its calendar
        page each run; start/end are the two days, the decision comes on
        end at 2:00 pm ET, and sep marks meetings with economic projections.
        If the page can't be read, the previous file's list is kept.

Usage: build_earnings_calendar.py [FEED ...] [--out PATH]
  FEEDs default to data/stocks/part-*.json; any {stocks: {...}} feed works,
  which is how a single list is tested locally.
"""

import argparse
import datetime
import glob
import html
import json
import re
import urllib.request
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
KEEP_DAYS = 7  # keep reports this many days back
FOMC_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
MONTHS = {m: i for i, m in enumerate(["January", "February", "March", "April", "May", "June", "July",
                                      "August", "September", "October", "November", "December"], 1)}


def fetch_fomc():
    """[{start, end, sep}] from the Fed's calendar page, or None on any failure.

    Each year's panel lists meetings as a month ("October", or "Apr/May" when
    a meeting spans two) and days ("27-28", with * when projections are
    released). Unscheduled or notation-vote entries have one day and no
    range; only two-day scheduled meetings are kept.
    """
    try:
        req = urllib.request.Request(FOMC_URL, headers={"User-Agent": "Mozilla/5.0"})
        page = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception as exc:
        print(f"FOMC: fetch failed ({type(exc).__name__}: {exc})")
        return None
    out = []
    for y, body in re.findall(r"(\d{4}) FOMC Meetings(.*?)(?=\d{4} FOMC Meetings|$)", page, re.S):
        for mon, days in re.findall(r"fomc-meeting__month[^>]*>\s*<strong>([^<]+)</strong>.*?"
                                    r"fomc-meeting__date[^>]*>([^<]+)<", body, re.S):
            mon, days = html.unescape(mon).strip(), html.unescape(days).strip()
            m = re.match(r"(\d+)-(\d+)(\*?)", days)
            names = [x.strip() for x in mon.split("/")]
            if not m or names[0] not in MONTHS:
                continue
            m1, m2 = MONTHS[names[0]], MONTHS.get(names[-1], MONTHS[names[0]])
            start = datetime.date(int(y), m1, int(m.group(1)))
            end = datetime.date(int(y), m2, int(m.group(2)))
            out.append({"start": start.isoformat(), "end": end.isoformat(), "sep": bool(m.group(3))})
    out.sort(key=lambda f: f["start"])
    year = str(datetime.datetime.now(ET).year)  # the page also lists past years
    out = [f for f in out if f["end"] >= year]
    if len(out) < 8:  # the page always carries at least the current year's eight
        print(f"FOMC: only {len(out)} meetings parsed; keeping the previous list")
        return None
    return out


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
            # US-dollar listings only: the International universe's local
            # listings (005930.KS, 6501.T) carry market caps in their own
            # currency, which would sort Samsung's won above Alphabet's
            # dollars. Their US ADRs, priced in dollars, stay.
            if t in seen or not d or d < cutoff or (s.get("cur") or "USD") != "USD":
                continue
            seen.add(t)
            r = {"t": t, "n": s.get("name") or t, "d": d}
            cap = s.get("marketCap")
            if isinstance(cap, (int, float)) and cap > 0:
                r["c"] = round(cap / 1e6)
            if s.get("earnDateEnd"):
                r["e"] = s["earnDateEnd"]
            if s.get("earnTime"):
                r["time"] = s["earnTime"]
            if s.get("earnEst"):
                r["est"] = True
            reports.append(r)
    reports.sort(key=lambda r: (r["d"], r["t"]))

    fomc = fetch_fomc()
    if fomc is None:
        try:
            with open(args.out, encoding="utf-8") as f:
                fomc = json.load(f).get("fomc") or []
        except (OSError, ValueError):
            fomc = []
    out = {"updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
           "source": "yahoo", "reports": reports, "fomc": fomc}
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
        f.write("\n")
    print(f"{len(reports)} upcoming reports, {len(fomc)} FOMC meetings, from {len(feeds)} feed(s) -> {args.out}")


if __name__ == "__main__":
    main()
