# TODO: Azqato Stock Methodology Site

Ideas and planned work not yet in the PRD roadmap. Move an item into the PRD (with a version) when it is scheduled.

---

## 0. WHAT IS LEFT AFTER v4.9.4 (updated 2026-09-29)

**v4.9.0 through v4.9.4 are all shipped, including the schedule cutover.** `stock-data.yml` now owns the daily stock data on two crons (curated universes Mon-Fri 21:37 UTC, whole market Sun 21:17 UTC), the four per-list feed workflows are deleted, and both halves of the Phase 0 gate passed. The parts pipeline is live rather than a snapshot.

### The one undecided item: the rolling statements schedule

`fetch_statements.py --universe --oldest-first 520` shipped in v4.9.2 and is **not scheduled**. `statements.yml` still runs weekly, Saturday 14:17 UTC, over the curated US lists only, so the roughly 3,050 stocks outside those lists have no statements at all.

To schedule it daily, a slot has to clear Market Overview's 15:07, 19:07 and 22:07 UTC runs, because statements sit in their own concurrency group and `fetch_statements.py` has **no push retry loop**, so an overlapping commit to `data/` loses the run's work. **02:17 UTC daily is the proposal and is undecided.** At 520 a night the universe comes round in 6.9 days.

Two things worth doing alongside, if that lands:
- Give `fetch_statements.py` the same rebase-retry push loop `stock-data.yml` uses, which would make the slot choice much less delicate.
- Decide whether 520 a night is right once the universe is 3,575 rather than 619, since the cadence is a policy choice, not a constraint.

### Watch for, now that both cadences are live

- **The first Sunday whole-market run** (Sunday 21:17 UTC, about 21 minutes over 8 parts). The daily half has run under the old per-list schedule for months at this minute; the weekly half has only ever run locally and by dispatch.
- **A new index member landing in a high part.** The daily matrix comes from `build_universe.py --parts-for`, so this should self-correct, but the first time `constituents.yml` adds a ticker after the cutover is the real test of both `--changed-parts` and `--parts-for` together.
- ~~**`check_workflow_health.py` reporting the retired workflows.**~~ Settled 2026-09-29: GitHub dropped all four from its workflow listing within hours, so v4.9.4's retired-workflow skip never had to carry them. Worth keeping for the next deletion.

**One post-cutover audit already happened (v4.9.5) and found three defects**, including a silent one that made the constituent sync's refetch dead code. Worth a second pass after the first Sunday run and the first post-cutover constituent change, since both exercise paths nothing has run yet.

### Verification already banked, worth not repeating

- Legacy feeds derive from the 8-part universe at 100% coverage for all six lists.
- The whole-market tier distribution was measured with screener.js's own scoring code under node: 14 S+ / 340 S / 362 A / 1,020 B / 871 C / 844 F over 3,451 scored of 3,465.
- The seven existing universes score identically to their committed feeds.
- The parts loader passes 10 of 10 checks, including with 6 of 8 parts deliberately absent.
- The plan job's matrix logic was extracted from the workflow YAML and run through all five branches (daily cron, weekly cron, manual with no input, manual with an explicit list, out-of-range part).
- All the node harnesses lived in the session scratchpad and are gone; they extracted functions from `screener.js` by source-text anchors and stubbed `fetch`, which is worth rebuilding the same way if this needs retesting.

---

## 1. One stock-data job for every list, in 500-stock parts (SCHEDULED)

**Moved into the PRD roadmap on 2026-09-28 as v4.9.0 through v4.9.3**, per this file's own rule that a scheduled item moves out of here and into the roadmap with a version. See `docs/PRD.md`, Roadmap, Open Milestone Detail, "One Stock-Data Job For Every List, In 500-Stock Parts" for the implementation plan.

The plan there keeps the owner's original design intact (one master universe, one record per ticker per day, parts of up to 500 ordered by importance, lists reduced to pure membership) and adds what costing it out turned up: parallel parts do conflict on push and need a rebase-retry loop, a 500-stock part runs in about 10 minutes rather than 30 to 45, parts weigh about 380 KB rather than 250 KB, the ETF feed stays separate because its records share only 7 of 20 fields with stock records, and the legacy per-list feeds keep being written permanently because v4.4.0's score-history sparklines mine their git history. The three owner decisions recorded here on 2026-09-28 (International stays at 100, VTI becomes its own "Total US market" list, one daily run time for everything) carry over unchanged, joined by a fourth: missing metrics keep scoring zero, with no coverage gate for the whole-market universe.

Nothing further is tracked here for this item.

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
