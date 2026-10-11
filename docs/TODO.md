# TODO: Azqato Stocks Data Feed

Ideas and planned work with no version yet. Move an item into the PRD (with a version) when it is scheduled. Cleaned up 2026-10-11 (v5.1.0): the shipped v4.9.x parts pipeline work was removed; its record is in PATCHNOTES.md.

---

## 1. The rolling statements schedule (undecided)

`fetch_statements.py --universe --oldest-first 520` shipped in v4.9.2 and is **not scheduled**. `statements.yml` still runs weekly, Saturday 14:17 UTC, over the curated US lists only, so the roughly 3,050 stocks outside those lists have no statements at all.

To schedule it daily, a slot has to clear Market Overview's 15:07, 19:07 and 22:07 UTC runs, because statements sit in their own concurrency group and `fetch_statements.py` has **no push retry loop**, so an overlapping commit to `data/` loses the run's work. **02:17 UTC daily is the proposal and is undecided.** At 520 a night the universe comes round in 6.9 days.

Two things worth doing alongside, if that lands:
- Give `fetch_statements.py` the same rebase-retry push loop `stock-data.yml` uses, which would make the slot choice much less delicate.
- Decide whether 520 a night is right once the universe is 3,575 rather than 619, since the cadence is a policy choice, not a constraint.

---

## 2. More fundamentals fields for Automate Fundamentals (owner request, 2026-09-29)

**Why.** Automate Fundamentals audited its 31 stock metrics (its PRD, "Fundamentals metrics audit (2026-09-29)", items FM1 to FM6). Most gaps are fields Yahoo already returns in the `Ticker.info` call each stock-data part makes, so adding them costs no extra requests. The screener can ignore them, as it does the v4.3.6 ratios.

**Check first (affects this screener too).** Yahoo documents `revenueGrowth` and `earningsGrowth` as the latest quarter versus the same quarter a year earlier, not trailing 12 months, and the screener labels them "Rev Growth TTM" and "EPS Growth TTM". Confirm against `quarterly_income_stmt`. If it holds, the label (and possibly the metric) is an owner decision here.

**Stock-record fields to add (from `info`, no extra requests):**
- TTM amounts (FM2): `totalRevenue`, `trailingEps`, `ebitda`, `netIncomeToCommon`, `freeCashflow` (FX-convert money fields the way cash and debt are).
- Ratios (FM3): `priceToBook`, `enterpriseToRevenue`, `enterpriseValue`, `trailingPegRatio`, `returnOnAssets`, `ebitdaMargins`, `quickRatio`, `payoutRatio`, `fiveYearAvgDividendYield`, `beta`, `shortPercentOfFloat`, `heldPercentInsiders`, `heldPercentInstitutions`, `targetMeanPrice`, `recommendationMean`, `numberOfAnalystOpinions`. Store fractions as percents, like the existing margins.
- Price trend for stocks (FM5): `fiftyTwoWeekHigh`, `fiftyTwoWeekLow`, `twoHundredDayAverage`, `52WeekChange`.

**Statement rows to add to `fetch_statements.py` (FM4):** interest expense, EBIT, stock-based compensation, and diluted average shares, for the TTM and fiscal-year columns. Automate Fundamentals computes ROIC, interest coverage, FCF margin, SBC share of revenue, share-count change, 3-year EPS CAGR, dividend growth, and net debt to EBITDA from them, and later Piotroski F and Altman Z (FM6).

**Size.** About 20 more fields, roughly 400 bytes a stock at `indent=2`, so about 200 KB more per 500-stock part.
