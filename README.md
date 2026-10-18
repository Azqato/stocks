# Azqato Stocks: Data Feed

Scheduled jobs that fetch public market data and publish it as JSON for [Azqato Invests](https://azqato.com/invests/) and Automate Fundamentals. The methodology pages moved to Azqato Invests on 2026-10-02; the old page addresses here only redirect there.

## What it publishes

Served at `azqato.github.io/stocks/data/`:

| Data | Written by | When (UTC) | Read by |
|------|-----------|-----------|---------|
| `stocks/` parts, `screener.json`, `screener_sp500.json`, `screener_gvd.json`, `screener_intl.json` | `stock-data.yml` | Mon-Fri 21:37; whole market Sun 21:17 | Invests Screener |
| `screener_etfs.json` (36 funds from `etfs.json`) | `screener-data-etfs.yml` | Mon-Fri 22:12 | Invests Screener (ETFs) |
| `market_overview.json` | `market-overview.yml` | Mon-Fri 15:07, 19:07, 22:07 | Invests Market Overview: 68 symbols, price, change, 52-week range, 10-day RSI; Fed Funds and CPI from FRED |
| `statements/<TICKER>.json` | `statements.yml` | daily 02:17, 1,000 oldest a night | Automate Fundamentals |
| Index and fund membership lists | `constituents.yml` | Sat 23:17 | the jobs above |

A failed job opens a GitHub issue (`alert-on-failure.yml`). Data comes from Yahoo Finance, Nasdaq, State Street and Vanguard; no API keys.

## Documentation

- [docs/PRD.md](docs/PRD.md): how the feed works: jobs, scripts, data models, scoring models, runbook
- [docs/PATCHNOTES.md](docs/PATCHNOTES.md): every change, newest first
- [docs/TODO.md](docs/TODO.md): ideas with no version yet

Educational use only. Not financial advice.
