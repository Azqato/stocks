# TODO: Azqato Stock Methodology Site

Ideas and planned work not yet in the PRD roadmap. Move an item into the PRD (with a version) when it is scheduled.

---

## 1. One stock-data job for every list, in 500-stock parts (SCHEDULED)

**Moved into the PRD roadmap on 2026-09-28 as v4.9.0 through v4.9.3**, per this file's own rule that a scheduled item moves out of here and into the roadmap with a version. See `docs/PRD.md`, Roadmap, Open Milestone Detail, "One Stock-Data Job For Every List, In 500-Stock Parts" for the implementation plan.

The plan there keeps the owner's original design intact (one master universe, one record per ticker per day, parts of up to 500 ordered by importance, lists reduced to pure membership) and adds what costing it out turned up: parallel parts do conflict on push and need a rebase-retry loop, a 500-stock part runs in about 10 minutes rather than 30 to 45, parts weigh about 380 KB rather than 250 KB, the ETF feed stays separate because its records share only 7 of 20 fields with stock records, and the legacy per-list feeds keep being written permanently because v4.4.0's score-history sparklines mine their git history. The three owner decisions recorded here on 2026-09-28 (International stays at 100, VTI becomes its own "Total US market" list, one daily run time for everything) carry over unchanged, joined by a fourth: missing metrics keep scoring zero, with no coverage gate for the whole-market universe.

Nothing further is tracked here for this item.
