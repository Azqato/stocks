# TODO — Azqato Stock Methodology Site

Ideas and planned work not yet in the PRD roadmap. Move an item into the PRD (with a version) when it is scheduled.

---

## 1. One stock-data job for every list, in 500-stock parts (owner idea, 2026-09-28)

**Why.** Six workflows fetch overlapping lists today (Nasdaq 100, S&P 500, Growth/Value/Dividend, International, ETFs, plus the weekly statements job from v4.3.6). A stock in four lists is fetched four times a day by different jobs. The owner also wants the whole US market (VTI) covered for Automate Fundamentals' Research page, which the per-list design cannot scale to.

**The idea.**

- **One master universe.** Every ticker in every list (`nasdaq100.json`, `sp500.json`, `vug.json`, `vtv.json`, `vig.json`, `vxus.json`, `etfs.json`, and later VTI), with duplicates removed.
- **One job, one record per ticker.** Each stock is fetched once per day, no matter how many lists hold it.
- **Lists become membership only.** Each list file stays exactly what it is: tickers and curated names. The screener picks a list, then looks each ticker up in the shared data. How a list is defined does not change; only where its numbers come from does.
- **Parts of up to 500 stocks.** The data is written as `data/stocks/part-01.json`, `part-02.json`, and so on. `data/stocks/index.json` maps each ticker to its part and records each part's `updated` time.
- **Parts ordered by importance, so the default view stays fast.**
  - Part 1 is the Nasdaq 100 plus the ETFs.
  - The next parts hold the rest of the S&P 500, then the Growth, Value, and Dividend lists, then International, then VTI.
  - The screener's default Nasdaq 100 view downloads one file, as it does today. The S&P 500 view downloads about 2.
  - Only a whole-market view would download everything.
  - A ticker keeps its part until it leaves every list, so parts do not reshuffle daily.
- **Parts run in parallel.** A GitHub Actions matrix runs one job per part, each within about 30 to 45 minutes. Each part commits only its own file, so the parts cannot conflict. Part 1 runs first, so the most-used view is fresh soonest, as the Nasdaq-first chain guarantees today.
- **Statements on a rolling week.** The per-stock statements (`data/statements/<TICKER>.json`) refresh a seventh of the stocks each day instead of all on Saturday. Every stock still refreshes weekly, and Yahoo sees an even daily load.

**Size check (VTI added).**

- About 4,000 US stocks plus 100 International plus 10 ETFs, which is about 9 parts.
- The daily data is about 500 bytes a stock, so about 250 KB a part.
- Yahoo load: one `info` call and two estimate calls per stock a day, plus about 600 statement fetches a day. That is higher than today, so the rollout should add VTI last, after the merge has run cleanly for a week.

**What has to change together.**

- `scripts/fetch_screener_data.py` gains a `--part N` mode; the six screener workflows become one matrix workflow.
- `screener.js` loads `index.json` and then only the parts a list needs, instead of one file per list.
- Scoring does not change: it already runs in the browser over whatever stocks the list holds.
- `constituents.yml` rebuilds the master universe and `index.json` when lists change.
- `alert-on-failure.yml` and `check_workflow_health.py` watch the new workflow name.
- **Automate Fundamentals** (`AzqatoFeedSource`) reads the old per-list files. Keep writing the old files for one transition release, then switch Automate Fundamentals to the parts in the same week.

**Open questions for the owner.**

1. Should International stay at the top 100 VXUS holdings? Full VXUS is about 8,500 stocks, which is too much for Yahoo, and Automate Fundamentals cannot trade most of them through Alpaca.
2. Is VTI wanted on the Azqato screener as its own list ("Total US market"), or only as data for Automate Fundamentals?
3. Is one combined daily time acceptable, or should the Nasdaq 100 part keep its own earlier schedule?
