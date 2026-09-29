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
- **`check_workflow_health.py` reporting the retired workflows.** It now skips any workflow GitHub still lists whose file is gone, but GitHub drops them from the listing eventually and that transition has not been observed.

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
