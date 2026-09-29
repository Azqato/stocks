# TODO: Azqato Stock Methodology Site

Ideas and planned work not yet in the PRD roadmap. Move an item into the PRD (with a version) when it is scheduled.

---

## 0. ONE STEP LEFT: the schedule cutover (updated 2026-09-29 01:10 UTC)

v4.9.0, v4.9.2 and v4.9.3 are all built, verified locally and pushed. The working tree is clean. **Everything now works locally, which was the owner's condition for considering the cutover.** What remains is one commit that nothing else depends on, and which was blocked once by auto mode as a production deploy.

### The cutover, file by file

1. **Delete** `.github/workflows/screener-data.yml`, `screener-data-sp500.yml`, `screener-data-gvd.yml`, `screener-data-intl.yml`. The ETFs job stays: ETF records share only 7 of their 20 fields with stock records and score on a different model.
2. **Add** `cron: "37 21 * * 1-5"` to `stock-data.yml`, the same minute the Nasdaq 100 job used, for the same reason (30 minutes after the latest possible US close in UTC terms, on an off-peak minute).
3. **Replace** `constituents.yml`'s four per-list regeneration blocks with one that runs `build_universe.py --changed-parts`, refetches only those parts, then derives the feeds. On a normal week that is one part or none.
4. **Remove** the four retired workflow names from `alert-on-failure.yml`, and their entries from `MAX_AGE_HOURS` in `check_workflow_health.py`.

**Rollback is reverting that one commit.** Nothing else in v4.9.x depends on it, which is why it was kept separate from the start.

### What the cutover unblocks

- The parts stop being a 2026-09-28 snapshot and refresh daily, which is what the whole-market universe needs to stay honest.
- `build_universe.py --changed-parts` gains its only caller.
- The rolling statements schedule (`--universe --oldest-first 520`) can replace the Saturday all-at-once run in `statements.yml`.

### The Phase 0 gate, as it actually stands

- **Statements half: passed.** 520 files at 20:37 UTC 2026-09-28, none truncated.
- **Daily-feed half: still open, and not for a worrying reason.** As of 01:06 UTC 2026-09-29 the Monday 21:37 UTC run had not fired at all. Every per-list workflow reads `success`, last run 2 to 3 days ago, so nothing is failing; this is the known multi-hour GitHub cron lag the owner decided on 2026-09-21 to leave alone. The committed feeds are still 2026-09-26 with 19 fields.
- **Mitigating evidence:** v4.3.6's nine ratio fields were produced correctly by every local part fetch, 3,575 symbols across 8 parts, so the untested surface is the CI environment rather than the code.

### Verification already banked, worth not repeating

- Legacy feeds derive from the 8-part universe at 100% coverage for all six lists.
- The whole-market tier distribution was measured with screener.js's own scoring code under node: 14 S+ / 340 S / 362 A / 1,020 B / 871 C / 844 F over 3,451 scored of 3,465.
- The seven existing universes score identically to their committed feeds.
- The parts loader passes 10 of 10 checks, including with 6 of 8 parts deliberately absent.
- Both node harnesses lived in the session scratchpad and are gone; they extracted functions from `screener.js` by source-text anchors and stubbed `fetch`, which is worth rebuilding the same way if this needs retesting.

---

## 1. One stock-data job for every list, in 500-stock parts (SCHEDULED)

**Moved into the PRD roadmap on 2026-09-28 as v4.9.0 through v4.9.3**, per this file's own rule that a scheduled item moves out of here and into the roadmap with a version. See `docs/PRD.md`, Roadmap, Open Milestone Detail, "One Stock-Data Job For Every List, In 500-Stock Parts" for the implementation plan.

The plan there keeps the owner's original design intact (one master universe, one record per ticker per day, parts of up to 500 ordered by importance, lists reduced to pure membership) and adds what costing it out turned up: parallel parts do conflict on push and need a rebase-retry loop, a 500-stock part runs in about 10 minutes rather than 30 to 45, parts weigh about 380 KB rather than 250 KB, the ETF feed stays separate because its records share only 7 of 20 fields with stock records, and the legacy per-list feeds keep being written permanently because v4.4.0's score-history sparklines mine their git history. The three owner decisions recorded here on 2026-09-28 (International stays at 100, VTI becomes its own "Total US market" list, one daily run time for everything) carry over unchanged, joined by a fourth: missing metrics keep scoring zero, with no coverage gate for the whole-market universe.

Nothing further is tracked here for this item.
