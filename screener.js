  (function () {
    "use strict";

    // The ticker universe comes from the loaded feed (data/screener.json), whose
    // constituents are sourced from data/nasdaq100.json -- a single source of truth,
    // so there is no embedded list to drift out of sync.
    function universe() {
      return Object.keys(data).map(function (t) { return [t, (data[t] && data[t].name) || t]; });
    }

    // The daily feeds are the single source of truth. Pull them straight from
    // GitHub (raw) so they work even when this file is opened locally; fall back
    // to the same-origin copy, then to a localStorage cache if the network is down.
    // The Nasdaq 100 is the default view; the other universes are lazy-loaded on
    // first use. Growth, Value, and Dividend share one combined feed file
    // (screener_gvd.json) keyed by `feedKey`, so one fetch fills all three.
    var RAW_BASE = "https://raw.githubusercontent.com/Azqato/stocks/main/data/";
    var GVD_PATHS = [RAW_BASE + "screener_gvd.json", "data/screener_gvd.json"];
    var UNIVERSES = {
      nasdaq100: {
        label: "Nasdaq 100",
        paths: [RAW_BASE + "screener.json", "data/screener.json"],
        cacheKey: "azq_screener_cache",
        store: null    // { stocks, updated, source } once loaded this session
      },
      sp500: {
        label: "S&P 500",
        paths: [RAW_BASE + "screener_sp500.json", "data/screener_sp500.json"],
        cacheKey: "azq_screener_sp500_cache",
        store: null
      },
      growth: {
        label: "Growth 100",           // top 100 VUG holdings
        paths: GVD_PATHS, feedKey: "growth",
        cacheKey: "azq_screener_growth_cache",
        store: null
      },
      value: {
        label: "Value 100",            // top 100 VTV holdings
        paths: GVD_PATHS, feedKey: "value",
        cacheKey: "azq_screener_value_cache",
        store: null
      },
      dividend: {
        label: "Dividend 100",         // top 100 VIG holdings
        paths: GVD_PATHS, feedKey: "dividend",
        cacheKey: "azq_screener_dividend_cache",
        store: null
      },
      etfs: {
        label: "ETFs",                 // fixed, owner-curated 10-fund list (data/etfs.json)
        kind: "etf",                   // different columns and scoring model (see ETF_METRICS)
        paths: [RAW_BASE + "screener_etfs.json", "data/screener_etfs.json"],
        cacheKey: "azq_screener_etfs_cache",
        store: null
      },
      intl: {
        label: "International",        // top 100 VXUS holdings (data/vxus.json)
        // Same six-metric stock model as the domestic universes; only the
        // feed differs (adds a `cur` field for native-currency price display).
        paths: [RAW_BASE + "screener_intl.json", "data/screener_intl.json"],
        cacheKey: "azq_screener_intl_cache",
        // Local-exchange tickers (005930.KS, 7203.T) aren't recognizable like
        // domestic ones, so this universe leads with the company name in the
        // ticker cell, popup title, and column header (v3.34.7). A no-op for
        // every other universe, which all leave this unset.
        nameFirst: true,
        store: null
      }
    };

    // ---- State ----
    var universeMode = "nasdaq100"; // active universe key
    var data = {};       // ticker -> metrics object (active universe)
    var meta = {};       // { updated: ISOString, source }
    var filter = "all";
    var sortKey = "score";
    var sortDir = -1;    // -1 desc, 1 asc
    var query = "";
    var feedDone = false; // true once the active universe's fetch has finished
    var toggling = false; // guard against double-clicks while a feed loads
    var mag10Active = false; // "MAG 10" watchlist toggle (v3.36.0), S&P 500 data only

    // Fixed 10-ticker watchlist (owner-supplied, 2026-07-04). Sourced from the
    // S&P 500 universe specifically -- toggling switches the active universe
    // to S&P 500 if needed, so each stock's score/tier reflects its percentile
    // among the full 500-stock set, not a smaller or differently-composed one.
    var MAG10_TICKERS = ["AAPL", "AMD", "AMZN", "AVGO", "GOOGL", "META", "MSFT", "NFLX", "NVDA", "TSLA"];

    // ---- DOM ----
    var $ = function (id) { return document.getElementById(id); };
    var tbody = $("tbody");

    // ---- Cache (offline fallback only; one key per universe) ----
    function readCache(key) {
      try { var c = JSON.parse(localStorage.getItem(key)); return (c && c.stocks) ? c : null; } catch (e) { return null; }
    }
    function writeCache(key, feed) {
      try { localStorage.setItem(key, JSON.stringify({ updated: feed.updated, source: feed.source, stocks: feed.stocks })); } catch (e) {}
    }
    function loadState() {
      // Seed the active universe from its offline cache so the table isn't blank
      // while the network fetch is in flight.
      var u = UNIVERSES[universeMode];
      var c = readCache(u.cacheKey);
      if (c) {
        u.store = { stocks: c.stocks, updated: c.updated, source: "cache" };
        data = c.stocks;
        meta = { updated: c.updated, source: "cache" };
      }
    }

    // ---- Number helpers ----
    function isNum(n) { return typeof n === "number" && isFinite(n); }
    function fmtPct(n) { return isNum(n) ? n.toFixed(1) + "%" : "—"; }
    function fmtNum(n) { return isNum(n) ? n.toFixed(2) : "—"; }
    // Currency symbol for $-formatted cells (v3.34.0 International universe).
    // Domestic universes never set `cur` (or set "USD"), so they format
    // exactly as before. Currencies with no widely recognized symbol (e.g.
    // CHF) fall back to printing the ISO code.
    var CURRENCY_SYMBOLS = {
      TWD: "NT$", KRW: "₩", EUR: "€", HKD: "HK$", GBP: "£",
      CAD: "C$", AUD: "A$", JPY: "¥", DKK: "kr", SEK: "kr", SGD: "S$", INR: "₹"
    };
    function currencyPrefix(cur) {
      if (!cur || cur === "USD") return "$";
      var sym = CURRENCY_SYMBOLS[cur];
      return sym !== undefined ? sym : (cur + " ");
    }
    function fmtMoney(n, cur) {
      if (!isNum(n)) return "—";
      var a = Math.abs(n), p = currencyPrefix(cur);
      if (a >= 1e12) return p + (n / 1e12).toFixed(2) + "T";
      if (a >= 1e9)  return p + (n / 1e9).toFixed(2) + "B";
      if (a >= 1e6)  return p + (n / 1e6).toFixed(1) + "M";
      if (a >= 1e3)  return p + (n / 1e3).toFixed(1) + "K";
      return p + n.toFixed(0);
    }
    function fmtPrice(n, cur) { return isNum(n) ? currencyPrefix(cur) + n.toFixed(2) : "—"; }
    function fmtChange(n) { return isNum(n) ? (n > 0 ? "+" : "") + n.toFixed(2) + "%" : "—"; }
    function fmtRet(n) { return isNum(n) ? (n > 0 ? "+" : "") + n.toFixed(1) + "%" : "—"; }   // signed returns (YTD, 1/5/10y, vs-MA)
    function fmtPct2(n) { return isNum(n) ? n.toFixed(2) + "%" : "—"; }                        // yield / expense ratio
    function fmtRsi(n) { return isNum(n) ? n.toFixed(1) : "—"; }
    function fmtRangePos(n) { return isNum(n) ? Math.round(n) + "%" : "—"; }                   // position within the 52-week range
    function clsChange(n) {
      if (!isNum(n) || n === 0) return "muted";
      return n > 0 ? "pos" : "neg";
    }
    function freshestMs(a, b) {
      var ta = a ? Date.parse(a) : 0, tb = b ? Date.parse(b) : 0;
      var m = Math.max(ta, tb);
      return m || null;
    }
    function fmtAge(ms) {
      if (!ms) return "—";
      var diff = Math.max(0, Date.now() - ms);
      var mins = Math.floor(diff / 60000);
      if (mins < 60) return mins + "m";
      var hrs = Math.floor(mins / 60);
      if (hrs < 24) return hrs + "h";
      return Math.floor(hrs / 24) + "d";
    }
    function clsAge(ms) { return (ms && Date.now() - ms > 8 * 86400000) ? "cau" : "muted"; }
    function ageTitle(d) {
      var p = d.priceUpdated ? new Date(d.priceUpdated).toLocaleString() : "—";
      var f = d.fundamentalsUpdated ? new Date(d.fundamentalsUpdated).toLocaleString() : "—";
      return "Price: " + p + "  •  Fundamentals: " + f;
    }

    // ---- Scoring: relative percentile model v3 (four even pillars) ----
    // Six metrics in four equally-weighted 25pt pillars: TTM (Rev TTM 10, EPS
    // TTM 15), FWD (Rev FWD 10, EPS FWD 15), Valuation 25 (PEG FWD), Balance
    // sheet 25 (cash vs debt). Deliberately weights trailing, proven growth
    // the same as forward analyst estimates (the prior model double-weighted
    // FWD over TTM within Growth), and gives Valuation and Balance sheet more
    // say -- a quality/value tilt over the prior model's growth tilt; owner
    // decision, chosen over keeping FWD double-weighted. Each metric's points
    // ramp with the stock's percentile rank among its loaded peers,
    // clamped at the top/bottom 22%: only the top 22% of a metric earns full
    // marks. The clamp is calibrated on live feeds so a perfect 100 stays
    // rare: roughly 1 stock in the Nasdaq 100 and 5 in the S&P 500, with more
    // only when rounded scores tie. Missing data scores a hard ZERO for that
    // metric -- the denominator stays 100, so an incomplete stock can never
    // outscore a complete one (its missing cell renders dark red).
    function clamp(x, lo, hi) { return x < lo ? lo : (x > hi ? hi : x); }
    var CLAMP_Q = 0.22; // full marks at the (1-q)th percentile, zero below the qth
    function pointsFromPct(p) { return clamp(20 * (p - CLAMP_Q) / (1 - 2 * CLAMP_Q), 0, 20); }

    // `weight` > 0 metrics feed the Score; weight-0 metrics (the P/E-vs-growth
    // context ratio) are ranked only so their cells can be colored by percentile.
    var METRICS = [
      { key: "revTTM",   weight: 10, higher: true,  get: function (d) { return isNum(d.revTTM) ? d.revTTM : null; } },
      { key: "revFwd",   weight: 10, higher: true,  get: function (d) { return isNum(d.revFwd) ? d.revFwd : null; } },
      { key: "epsTTM",   weight: 15, higher: true,  get: function (d) { return isNum(d.epsTTM) ? d.epsTTM : null; } },
      { key: "epsFwd",   weight: 15, higher: true,  get: function (d) { return isNum(d.epsFwd) ? d.epsFwd : null; } },
      { key: "peVsG",    weight: 0,  higher: false, get: function (d) {
          if (!isNum(d.peFwd) || !isNum(d.epsFwd)) return null;
          // Unprofitable (P/E <= 0) or shrinking earnings (growth <= 0) rank worst, not best/dropped.
          return (d.peFwd <= 0 || d.epsFwd <= 0) ? Infinity : d.peFwd / d.epsFwd;
        } },
      { key: "pegFwd",   weight: 25, higher: false, get: function (d) {
          if (isNum(d.peFwd) && d.peFwd <= 0) return Infinity; // unprofitable: Yahoo PEG is unreliable, rank worst
          return (isNum(d.pegFwd) && d.pegFwd > 0) ? d.pegFwd : null;
        } },
      { key: "cashDebt", weight: 25, higher: true,  get: function (d) { if (!isNum(d.cash) || !isNum(d.debt)) return null; return d.debt === 0 ? (d.cash > 0 ? Infinity : null) : d.cash / d.debt; } },
      // Context only (weight 0): ranked so the column can be percentile-colored,
      // but contributes nothing to the score (scoredCount counts weight > 0).
      { key: "netCashMc", weight: 0,  higher: true,  get: function (d) { return netCashToMktCap(d); } }
    ];

    // ---- ETFs universe scoring (v3.33.0): a different model for a different question ----
    // The stock universes grade fundamentals; the ETFs list is timed with
    // technicals, per the site doctrine (technicals time index/ETF purchases).
    // Six scored metrics (v3.37.0, owner decision 2026-07-04): Technicals 50
    // (RSI 20, 52-week range position 20, price vs 200-day MA 10), Performance
    // 50 (1-year total return 10, 5-year 20, 10-year 20 -- weighted toward the
    // longer horizons since indices.html calls the 10-year return "the most
    // durable signal," evidence the outperformance is structural, not luck).
    // Yield and Expense Ratio were removed from scoring the same day (no
    // longer aligned with the reviewed methodology) and demoted to weight-0
    // context, alongside YTD, net yield, and the 20/100-day MA columns --
    // colored rankings with no points, like P/E FWD in the stock model; AUM
    // is display-only. With just 10 funds a percentile clamp is far too
    // coarse, so points are straight rank-linear: the best fund on a metric
    // earns 20, the worst 0, evenly spaced, ties averaged (see the curve
    // selection in computeScoreMap).
    function wk52Pos(d) {
      if (!isNum(d.price) || !isNum(d.wk52Low) || !isNum(d.wk52High) || d.wk52High <= d.wk52Low) return null;
      return clamp((d.price - d.wk52Low) / (d.wk52High - d.wk52Low) * 100, 0, 100);
    }
    function netYield(d) {
      if (!isNum(d.yieldPct) || !isNum(d.expenseRatio)) return null;
      return d.yieldPct - d.expenseRatio;
    }
    var ETF_METRICS = [
      { key: "rsi",          weight: 20, higher: false, get: function (d) { return isNum(d.rsi) ? d.rsi : null; } },
      { key: "wk52",         weight: 20, higher: false, get: function (d) { return wk52Pos(d); } },
      { key: "ret1y",        weight: 10, higher: true,  get: function (d) { return isNum(d.ret1y) ? d.ret1y : null; } },
      { key: "ret5y",        weight: 20, higher: true,  get: function (d) { return isNum(d.ret5y) ? d.ret5y : null; } },
      { key: "ret10y",       weight: 20, higher: true,  get: function (d) { return isNum(d.ret10y) ? d.ret10y : null; } },
      { key: "pctVs200dma",  weight: 10, higher: true,  get: function (d) { return isNum(d.pctVs200dma) ? d.pctVs200dma : null; } },
      { key: "ytd",          weight: 0,  higher: true,  get: function (d) { return isNum(d.ytd) ? d.ytd : null; } },
      { key: "yieldPct",     weight: 0,  higher: true,  get: function (d) { return isNum(d.yieldPct) ? d.yieldPct : null; } },
      { key: "expenseRatio", weight: 0,  higher: false, get: function (d) { return isNum(d.expenseRatio) ? d.expenseRatio : null; } },
      { key: "netYield",     weight: 0,  higher: true,  get: function (d) { return netYield(d); } },
      { key: "pctVs20dma",   weight: 0,  higher: true,  get: function (d) { return isNum(d.pctVs20dma) ? d.pctVs20dma : null; } },
      { key: "pctVs100dma",  weight: 0,  higher: true,  get: function (d) { return isNum(d.pctVs100dma) ? d.pctVs100dma : null; } }
    ];

    function modeKind() { return UNIVERSES[universeMode].kind || "stock"; }
    function isEtf() { return modeKind() === "etf"; }
    function activeMetrics() { return isEtf() ? ETF_METRICS : METRICS; }

    // Rank every loaded stock on each metric, convert ranks to points, and sum.
    // `parts` keeps every metric's points on a 0-20 scale (for cell colors and
    // the popup); the total applies each metric's weight.
    function computeScoreMap() {
      var ms = activeMetrics();
      // ETFs use straight rank-linear points (best 20, worst 0); the stock
      // universes use the calibrated percentile clamp above.
      var curve = isEtf() ? function (p) { return 20 * p; } : pointsFromPct;
      var totalWeight = ms.reduce(function (s, m) { return s + m.weight; }, 0);   // 100 in both modes
      var scoredCount = ms.filter(function (m) { return m.weight > 0; }).length;  // 6 stocks, 8 ETFs

      var tickers = Object.keys(data);
      var pts = {};   // ticker -> { metricKey: points 0-20 }
      var pcts = {};  // ticker -> { metricKey: percentile 0..1 }
      tickers.forEach(function (t) { pts[t] = {}; pcts[t] = {}; });

      ms.forEach(function (m) {
        var vals = [];
        tickers.forEach(function (t) {
          var d = data[t];
          if (!d) return;
          var v = m.get(d);
          if (v === null || v === undefined) return;
          vals.push({ t: t, v: v });
        });
        var n = vals.length;
        if (!n) return;
        vals.sort(function (a, b) { return a.v === b.v ? 0 : (a.v < b.v ? -1 : 1); });
        var i = 0;
        while (i < n) {
          var j = i;
          while (j + 1 < n && vals[j + 1].v === vals[i].v) j++; // average-rank ties
          var perc = n > 1 ? ((i + j) / 2) / (n - 1) : 0.5;
          if (!m.higher) perc = 1 - perc; // lower-is-better metrics invert
          var p = curve(perc);
          for (var k = i; k <= j; k++) { pts[vals[k].t][m.key] = p; pcts[vals[k].t][m.key] = perc; }
          i = j + 1;
        }
      });

      var out = {};
      tickers.forEach(function (t) {
        var sum = 0, have = 0, passes = 0;
        ms.forEach(function (m) {
          if (!m.weight) return;
          var p = pts[t][m.key];
          if (p === undefined) return; // missing = hard zero (adds nothing, denominator stays 100)
          have++;
          sum += p * (m.weight / 20);
          if (p >= 15) passes++; // upper part of the pack on that metric
        });
        if (!have) { out[t] = { pct: null, passes: 0, total: 0, parts: pts[t], pctiles: pcts[t] }; return; }
        out[t] = {
          pct: Math.round(sum / totalWeight * 100),
          passes: passes,
          total: scoredCount, // fixed denominator: a missing metric is a miss, not a pass
          parts: pts[t],   // percentile points per metric (0-20 scale), for cell coloring
          pctiles: pcts[t] // raw percentiles, for the per-stock breakdown popup
        };
      });
      return out;
    }
    // Cell color from a metric's percentile points: top of the pack green,
    // bottom red, middle amber. The stock clamp already sends its top/bottom
    // 22% to exactly 20/0; ETF rank-linear points only hit those extremes for
    // the single best/worst fund, so ETF mode colors the top and bottom ~3.
    function colorFromPts(p) {
      if (p === undefined || p === null) return "muted";
      var hi = isEtf() ? 15 : 20, lo = isEtf() ? 5 : 0;
      if (p >= hi) return "pos";
      if (p <= lo) return "neg";
      return "cau";
    }
    // Scored metrics: missing data is a hard zero, so a "—" renders dark red.
    function colorScored(p) {
      if (p === undefined || p === null) return "neg";
      return colorFromPts(p);
    }
    // Tier list by rank (v3.29.0): S = top 10% of the scored stocks in the
    // loaded list, A = next 10%, B = 20-50%, C = 50-75%, F = bottom 25%.
    // A ranking, not a buy/sell rating. Boundary ties round UP: every stock
    // whose (rounded) score matches the last stock inside a band joins that
    // band, so a tier only stretches past its quota on identical scores.
    // On top of the bands, a perfect 100/100 earns S+ (v3.30.0) -- those
    // stocks come out of the S band's headcount, they don't push it down.
    var TIER_CUTS = [["s", 0.10], ["a", 0.20], ["b", 0.50], ["c", 0.75]]; // f = the rest
    function computeTierMap(sm) {
      var order = Object.keys(sm)
        .filter(function (t) { return sm[t].pct !== null; })
        .sort(function (a, b) { return sm[b].pct - sm[a].pct; });
      var n = order.length;
      var tiers = {};
      if (!n) return tiers;
      var cuts = TIER_CUTS.map(function (c) { return Math.max(1, Math.round(c[1] * n)); });
      for (var k = 0; k < cuts.length; k++) {
        var j = Math.min(cuts[k], n) - 1;              // last stock inside the band
        var boundary = sm[order[j]].pct;
        while (j + 1 < n && sm[order[j + 1]].pct === boundary) j++; // ties round up
        cuts[k] = j + 1;
        if (k > 0 && cuts[k] < cuts[k - 1]) cuts[k] = cuts[k - 1];
      }
      var ci = 0;
      for (var i = 0; i < n; i++) {
        while (ci < cuts.length && i >= cuts[ci]) ci++;
        tiers[order[i]] = sm[order[i]].pct >= 100 ? "sp"
          : (ci < TIER_CUTS.length ? TIER_CUTS[ci][0] : "f");
      }
      return tiers;
    }

    // ---- Value + format helpers (cell colors are percentile-based; see colorFromPts) ----
    // For unprofitable companies (negative forward P/E), Yahoo's positive PEG is
    // misleading, so display our own forward PEG = P/E / EPS growth (negative).
    function pegDisplay(d) {
      if (isNum(d.peFwd) && d.peFwd <= 0 && isNum(d.epsFwd) && d.epsFwd > 0) return d.peFwd / d.epsFwd;
      return isNum(d.pegFwd) ? d.pegFwd : null;
    }
    function cashDebtRatio(d) {
      if (!isNum(d.cash) || !isNum(d.debt)) return null;
      if (d.debt > 0) return d.cash / d.debt;
      return d.cash > 0 ? Infinity : null; // no debt = effectively unbounded
    }
    // Net cash (cash minus debt) as a percentage of market cap. Positive = the
    // company holds more cash than debt worth this share of its value; negative
    // = net debt. Stored ×100 to match the growth-rate columns (fmtPct expects
    // percent units). Context only, not scored.
    function netCashToMktCap(d) {
      if (!isNum(d.cash) || !isNum(d.debt) || !isNum(d.marketCap) || d.marketCap <= 0) return null;
      return (d.cash - d.debt) / d.marketCap * 100;
    }
    function fmtRatio(n) {
      if (n === null || n === undefined || (typeof n === "number" && isNaN(n))) return "—";
      if (!isFinite(n)) return "∞"; // no debt
      return n.toFixed(2) + "x";
    }
    // The score bar takes its color from the stock's tier (tiers are ranks,
    // so the same score can be a different color in a different universe).
    var TIER_COLOR = {
      sp: "var(--color-tier-splus)",
      s: "var(--color-tier-s)", a: "var(--color-tier-a)", b: "var(--color-tier-b)",
      c: "var(--color-tier-c)", f: "var(--color-negative)", none: "var(--color-border)"
    };

    // ---- Build a renderable row model ----
    function rows() {
      var sm = computeScoreMap();
      var tiers = computeTierMap(sm);
      var etf = isEtf();
      return universe().map(function (s) {
        var t = s[0];
        var d = data[t] || {};
        var sc = sm[t] || { pct: null, passes: 0, total: 0, parts: {} };
        var r = {
          ticker: t, name: s[1], d: d, parts: sc.parts || {},
          score: sc.pct, passes: sc.passes, total: sc.total,
          tier: sc.pct === null ? "none" : tiers[t],
          price: d.price,
          changePct: isNum(d.changePct) ? d.changePct : null,
          updated: freshestMs(d.priceUpdated, d.fundamentalsUpdated)
        };
        if (etf) {
          r.aum = d.aum; r.ytd = d.ytd;
          r.ret1y = d.ret1y; r.ret5y = d.ret5y; r.ret10y = d.ret10y;
          r.yieldPct = d.yieldPct; r.expenseRatio = d.expenseRatio; r.netYield = netYield(d);
          r.rsi = d.rsi; r.wk52 = wk52Pos(d);
          r.pctVs20dma = d.pctVs20dma; r.pctVs100dma = d.pctVs100dma; r.pctVs200dma = d.pctVs200dma;
        } else {
          r.revTTM = d.revTTM; r.revFwd = d.revFwd; r.epsTTM = d.epsTTM; r.epsFwd = d.epsFwd;
          r.peFwd = d.peFwd; r.pegFwd = pegDisplay(d); r.cash = d.cash; r.debt = d.debt;
          r.cashDebt = cashDebtRatio(d); r.marketCap = d.marketCap;
          r.netCashMc = netCashToMktCap(d);
          r.cur = d.cur; // native currency code (International universe only; USD elsewhere)
        }
        return r;
      });
    }

    var TIER_RANK = { sp: 6, s: 5, a: 4, b: 3, c: 2, f: 1, none: 0 };

    function sortRows(rs) {
      var k = sortKey, dir = sortDir;
      return rs.slice().sort(function (a, b) {
        var av, bv;
        // International sorts this column by the name it visually leads with;
        // every other universe keeps sorting by ticker (unchanged behavior).
        if (k === "ticker") {
          return (isNameFirst() ? a.name.localeCompare(b.name) : a.ticker.localeCompare(b.ticker)) * dir;
        }
        if (k === "tier") { av = TIER_RANK[a.tier]; bv = TIER_RANK[b.tier]; }
        else if (k === "factors") { av = a.total ? a.passes / a.total : -1; bv = b.total ? b.passes / b.total : -1; }
        else { av = a[k]; bv = b[k]; }
        // For valuation columns a negative P/E or PEG is "worst" (unprofitable),
        // so sort it like a very high value rather than a cheap low one.
        if (k === "peFwd" || k === "pegFwd") {
          if (typeof av === "number" && av <= 0) av = Infinity;
          if (typeof bv === "number" && bv <= 0) bv = Infinity;
        }
        // "present" = a real number, including Infinity (e.g. cash/debt with no debt)
        var an = typeof av === "number" && !isNaN(av);
        var bn = typeof bv === "number" && !isNaN(bv);
        if (!an && !bn) return 0;
        if (!an) return 1;   // missing always sinks to bottom
        if (!bn) return -1;
        if (av === bv) return 0;
        return (av - bv) * dir;
      });
    }

    // ---- Render ----
    function render() {
      var rs = rows();

      // tier counts
      var counts = { all: rs.length, sp: 0, s: 0, a: 0, b: 0, c: 0, f: 0 };
      rs.forEach(function (r) { if (counts[r.tier] !== undefined) counts[r.tier]++; });
      $("cnt-all").textContent = counts.all;
      ["sp", "s", "a", "b", "c", "f"].forEach(function (t) { $("cnt-" + t).textContent = counts[t]; });

      // filter
      var view = rs.filter(function (r) {
        if (filter !== "all" && r.tier !== filter) return false;
        if (mag10Active && MAG10_TICKERS.indexOf(r.ticker) === -1) return false;
        if (query) {
          var q = query.toLowerCase();
          if (r.ticker.toLowerCase().indexOf(q) === -1 && r.name.toLowerCase().indexOf(q) === -1) return false;
        }
        return true;
      });
      view = sortRows(view);

      tbody.innerHTML = view.map(rowHtml).join("");

      // summary + placeholder
      var loaded = Object.keys(data).length;
      $("placeholder").style.display = (feedDone && loaded === 0) ? "flex" : "none";
      var scored = rs.filter(function (r) { return r.score !== null; }).length;
      if (loaded === 0) {
        $("summary").innerHTML = feedDone ? "No data" : "Loading the " + UNIVERSES[universeMode].label + "&hellip;";
      } else {
        $("summary").innerHTML = (counts.sp ? "<b>" + counts.sp + "</b> S+ &middot; " : "") +
          "<b>" + counts.s + "</b> S &middot; <b>" + counts.a + "</b> A &middot; <b>" +
          counts.b + "</b> B &middot; <b>" + counts.c + "</b> C &middot; <b>" + counts.f + "</b> F &middot; " +
          scored + "/" + loaded + " scored";
      }
      $("asOf").textContent = meta.updated ? "as of " + new Date(meta.updated).toLocaleString() : "no data loaded";

      applyColumnVisibility();
      updateSortIndicators();
      checkStale();
    }

    // ---- Daily feed (data/screener.json, refreshed by the GitHub Action) ----
    // Threshold is 7 days, not 24 hours: the daily refresh can slip a day or
    // two (weekends, a rate-limited run) without it being worth alarming the
    // user -- only a genuinely stuck pipeline (a week+) warrants the banner.
    function isStale(ts) {
      if (!ts) return true;
      return (Date.now() - new Date(ts).getTime()) > 7 * 24 * 3600 * 1000;
    }

    function checkStale() {
      var has = Object.keys(data).length > 0;
      var stale = has && isStale(meta.updated);
      $("staleBanner").classList.toggle("on", stale);
      if (stale) {
        $("staleText").innerHTML = meta.updated
          ? "This data is from " + new Date(meta.updated).toLocaleString() + " (more than a week old). The daily refresh may not have run."
          : "This data has no timestamp and may be out of date.";
      }
    }

    // Fetch a universe's feed from GitHub (works locally too), caching it for
    // offline use. Returns the in-memory store {stocks, updated, source} or null
    // if every source failed. Does not change the active view by itself.
    // Universes with a `feedKey` live inside the combined GVD file: the wanted
    // universe is extracted, and the siblings that came along in the same file
    // are stored and cached too, so switching between them needs no new fetch.
    async function fetchUniverse(key) {
      var u = UNIVERSES[key];
      for (var i = 0; i < u.paths.length; i++) {
        try {
          var res = await fetch(u.paths[i], { cache: "no-store" });
          if (!res.ok) continue;
          var body = await res.json();
          var feed = u.feedKey ? (body && body.universes && body.universes[u.feedKey]) : body;
          if (feed && feed.stocks && Object.keys(feed.stocks).length) {
            u.store = { stocks: feed.stocks, updated: feed.updated, source: feed.source || "feed" };
            writeCache(u.cacheKey, feed);
            if (u.feedKey) {
              Object.keys(UNIVERSES).forEach(function (k) {
                var o = UNIVERSES[k];
                if (k === key || !o.feedKey) return;
                var sib = body.universes[o.feedKey];
                if (sib && sib.stocks && Object.keys(sib.stocks).length) {
                  o.store = { stocks: sib.stocks, updated: sib.updated, source: sib.source || "feed" };
                  writeCache(o.cacheKey, sib);
                }
              });
            }
            return u.store;
          }
        } catch (e) { /* try the next source */ }
      }
      return null;
    }

    // ---- Per-mode table header and column groups ----
    // The stock and ETF universes show entirely different column sets, so the
    // <thead> and the Columns menu are re-rendered when the mode kind changes
    // (the static HTML ships the stock variant for first paint). Sort clicks
    // and Columns-menu changes are bound by delegation in bind(), so they
    // survive the re-render.
    var HEADS = {
      stock: {
        group: '<th class="col-ticker"></th>' +
          '<th class="g-screen group-start" colspan="3">Azqato Screen</th>' +
          '<th class="grp-snapshot group-start" colspan="3">Snapshot</th>' +
          '<th class="grp-growth group-start" colspan="4">Growth</th>' +
          '<th class="grp-valuation group-start" colspan="2">Valuation</th>' +
          '<th class="grp-balance group-start" colspan="4">Balance Sheet</th>' +
          '<th class="grp-snapshot group-start" colspan="1"></th>',
        head: '<th class="left col-ticker" data-sort="ticker">Ticker</th>' +
          '<th class="left group-start" data-sort="tier" title="Rank within the loaded list: S+ = a perfect 100 score, S = top 10%, A = next 10%, B = 20-50%, C = 50-75%, F = bottom 25%. Boundary ties round up.">Tier</th>' +
          '<th data-sort="score">Score</th>' +
          '<th data-sort="factors" title="Number of the 6 scored metrics ranking in the upper part of the pack (15+ of 20 percentile points)">Factors</th>' +
          '<th class="grp-snapshot group-start" data-sort="marketCap">Mkt Cap</th>' +
          '<th class="grp-snapshot" data-sort="price">Price</th>' +
          '<th class="grp-snapshot" data-sort="changePct" title="Change vs the prior session\'s close, as of the last daily data refresh">Chg %</th>' +
          '<th class="grp-growth group-start" data-sort="revTTM">Rev TTM</th>' +
          '<th class="grp-growth" data-sort="revFwd">Rev FWD</th>' +
          '<th class="grp-growth" data-sort="epsTTM">EPS TTM</th>' +
          '<th class="grp-growth" data-sort="epsFwd" title="GAAP-basis forward EPS growth (current fiscal year). May differ from Seeking Alpha, which uses Non-GAAP consensus.">EPS FWD*</th>' +
          '<th class="grp-valuation group-start" data-sort="peFwd" title="Shown for context and colored by the P/E-vs-growth ranking; the score\'s valuation points come from PEG FWD">P/E FWD</th>' +
          '<th class="grp-valuation" data-sort="pegFwd">PEG FWD</th>' +
          '<th class="grp-balance group-start" data-sort="cash">Total Cash</th>' +
          '<th class="grp-balance" data-sort="debt">Total Debt</th>' +
          '<th class="grp-balance" data-sort="cashDebt">Cash/Debt</th>' +
          '<th class="grp-balance" data-sort="netCashMc" title="Net cash (Total Cash minus Total Debt) as a percentage of market cap. Positive = net cash, negative = net debt. Colored by rank vs peers; context only, not scored.">Net Cash/Mkt Cap</th>' +
          '<th class="grp-snapshot group-start" data-sort="updated">Updated</th>'
      },
      etf: {
        group: '<th class="col-ticker"></th>' +
          '<th class="g-screen group-start" colspan="3">Azqato Screen</th>' +
          '<th class="grp-snapshot group-start" colspan="3">Snapshot</th>' +
          '<th class="grp-performance group-start" colspan="4">Performance</th>' +
          '<th class="grp-income group-start" colspan="3">Income &amp; Cost</th>' +
          '<th class="grp-technicals group-start" colspan="5">Technicals</th>' +
          '<th class="grp-snapshot group-start" colspan="1"></th>',
        head: '<th class="left col-ticker" data-sort="ticker">Fund</th>' +
          '<th class="left group-start" data-sort="tier" title="Rank within this 10-fund list: S+ = a perfect 100 score, S = top 10%, A = next 10%, B = 20-50%, C = 50-75%, F = bottom 25%. Boundary ties round up.">Tier</th>' +
          '<th data-sort="score">Score</th>' +
          '<th data-sort="factors" title="Number of the 6 scored metrics ranking in the upper part of the pack (15+ of 20 rank points)">Factors</th>' +
          '<th class="grp-snapshot group-start" data-sort="aum" title="Assets under management">AUM</th>' +
          '<th class="grp-snapshot" data-sort="price">Price</th>' +
          '<th class="grp-snapshot" data-sort="changePct" title="Change vs the prior session\'s close, as of the last daily data refresh">Chg %</th>' +
          '<th class="grp-performance group-start" data-sort="ytd" title="Year-to-date total return, distributions reinvested. Context only, not scored.">YTD</th>' +
          '<th class="grp-performance" data-sort="ret1y" title="1-year total return, distributions reinvested">1Y TR</th>' +
          '<th class="grp-performance" data-sort="ret5y" title="5-year total return, distributions reinvested. Weighted double the 1-year return -- a longer track record is stronger evidence of durable performance.">5Y TR</th>' +
          '<th class="grp-performance" data-sort="ret10y" title="10-year total return, distributions reinvested. Weighted double the 1-year return -- indices.html calls the 10-year return the most durable signal that outperformance is structural, not luck.">10Y TR</th>' +
          '<th class="grp-income group-start" data-sort="yieldPct" title="Trailing distribution yield. Context only, not scored.">Yield</th>' +
          '<th class="grp-income" data-sort="expenseRatio" title="Net expense ratio: the fund\'s annual cost. Context only, not scored.">Exp Ratio</th>' +
          '<th class="grp-income" data-sort="netYield" title="Yield minus expense ratio: what the distribution pays after the fund\'s cost. Context only, not scored.">Yld&minus;ER</th>' +
          '<th class="grp-technicals group-start" data-sort="rsi" title="14-day RSI. In this methodology a low RSI marks the better index/ETF entry, so lower scores higher.">RSI</th>' +
          '<th class="grp-technicals" data-sort="wk52" title="Where the price sits in its 52-week range (0% = at the low, 100% = at the high). Lower scores higher.">52W Range</th>' +
          '<th class="grp-technicals" data-sort="pctVs20dma" title="Price vs its 20-day moving average (short-term trend). Context only, not scored.">vs 20D</th>' +
          '<th class="grp-technicals" data-sort="pctVs100dma" title="Price vs its 100-day moving average (medium-term trend). Context only, not scored.">vs 100D</th>' +
          '<th class="grp-technicals" data-sort="pctVs200dma" title="Price vs its 200-day moving average (long-term trend). Scored: higher is better.">vs 200D</th>' +
          '<th class="grp-snapshot group-start" data-sort="updated">Updated</th>'
      }
    };
    var COL_GROUPS = {
      stock: [["snapshot", "Snapshot"], ["growth", "Growth"], ["valuation", "Valuation"], ["balance", "Balance Sheet"]],
      etf: [["snapshot", "Snapshot"], ["performance", "Performance"], ["income", "Income &amp; Cost"], ["technicals", "Technicals"]]
    };
    function renderHead() {
      var h = HEADS[modeKind()];
      document.querySelector("#table thead").innerHTML =
        '<tr class="group-row">' + h.group + '</tr><tr class="head-row">' + h.head + '</tr>';
    }
    function renderColsMenu() {
      $("colsMenu").innerHTML = COL_GROUPS[modeKind()].map(function (g) {
        return '<label><input type="checkbox" data-group="' + g[0] + '" checked> ' + g[1] + '</label>';
      }).join("");
    }

    // International (v3.34.7) relabels the ticker column "Company" without a
    // full HEADS/renderHead() rebuild -- it shares "stock" kind with the five
    // domestic universes, so renderHead() only fires on nasdaq100<->etfs-style
    // kind changes, never on a same-kind switch like nasdaq100<->intl. ETF
    // mode's own "Fund" label comes from its own HEADS entry and is untouched
    // here. Safe to call on every render(): the arrow indicator this might
    // clobber is unconditionally rebuilt by updateSortIndicators() right after.
    function updateTickerColumnLabel() {
      if (isEtf()) return;
      var th = document.querySelector('#table thead tr.head-row th[data-sort="ticker"]');
      if (th) th.textContent = isNameFirst() ? "Company" : "Ticker";
    }

    // Point data/meta at a universe's dataset, swap the on-screen labels, repaint.
    function activate(key, store) {
      var prevKind = modeKind();
      universeMode = key;
      if (modeKind() !== prevKind) {
        // Different column set: rebuild the header and Columns menu, and drop
        // any sort keyed to a column that no longer exists.
        renderHead();
        renderColsMenu();
        applyResponsiveColumns();
        sortKey = "score";
        sortDir = -1;
      }
      updateTickerColumnLabel();
      data = {};
      Object.keys(store.stocks).forEach(function (k) { data[k] = store.stocks[k]; });
      meta = { updated: store.updated, source: store.source };
      setUniverseLabel(UNIVERSES[key].label);
      updateUniverseButtons();
      render();
    }

    // Swap every universe label (and the page title) to match the view.
    function setUniverseLabel(label) {
      document.querySelectorAll(".universe-name").forEach(function (el) { el.textContent = label; });
      document.title = label + " Screener";
    }

    // Light up the active universe's button.
    function updateUniverseButtons() {
      document.querySelectorAll("#universeGroup .u-btn").forEach(function (b) {
        b.classList.toggle("active", b.getAttribute("data-universe") === universeMode);
      });
    }

    function setUniverseButtonsDisabled(on) {
      document.querySelectorAll("#universeGroup .u-btn").forEach(function (b) { b.disabled = on; });
    }

    // Initial page load: fetch the default Nasdaq 100 feed.
    async function loadInitial() {
      var store = await fetchUniverse("nasdaq100");
      feedDone = true;
      if (store) activate("nasdaq100", store);
      else render(); // network failed: keep whatever the startup cache gave us
    }

    // Buttons: switch to a universe, lazy-loading its feed on first use.
    async function selectUniverse(target) {
      if (toggling || target === universeMode || !UNIVERSES[target]) return;
      var u = UNIVERSES[target];

      if (u.store) { activate(target, u.store); return; } // already in memory -> instant

      toggling = true;
      setUniverseButtonsDisabled(true);
      $("summary").innerHTML = "Loading the " + u.label + "&hellip;";

      var store = await fetchUniverse(target);
      toggling = false;
      setUniverseButtonsDisabled(false);

      if (store) {
        activate(target, store);
      } else {
        // Feed not generated yet (or offline): stay on the current view, explain why.
        render();
        $("summary").innerHTML = u.label + " data isn’t available yet — it’s generated by " +
          "the daily update. Check back after the next refresh.";
      }
    }

    // ---- MAG 10 watchlist toggle (v3.36.0) ----
    function updateMag10Button() {
      $("mag10Btn").classList.toggle("active", mag10Active);
    }
    async function toggleMag10() {
      if (!mag10Active) {
        if (universeMode !== "sp500") await selectUniverse("sp500");
        mag10Active = true;
      } else {
        mag10Active = false;
      }
      updateMag10Button();
      render();
    }

    var TIER_LABEL = { sp: "S+", s: "S", a: "A", b: "B", c: "C", f: "F", none: "NO DATA" };

    function isNameFirst() { return !!UNIVERSES[universeMode].nameFirst; }

    // The Ticker / Tier / Score / Factors cells are identical in both modes.
    function screenCells(r) {
      var scoreCell;
      if (r.score === null) {
        scoreCell = '<span class="muted">—</span>';
      } else {
        scoreCell = '<span class="score-bar-wrap"><span class="score-val">' + r.score + '</span>' +
          '<span class="score-track"><span class="score-fill" style="width:' + r.score + '%;background:' +
          TIER_COLOR[r.tier] + '"></span></span></span>';
      }
      var factorsCell = r.total ? '<span class="factors">' + r.passes + "/" + r.total + "</span>" : '<span class="muted">—</span>';
      // International leads with the company name (local-exchange tickers like
      // 005930.KS aren't recognizable); every other universe keeps ticker-first.
      var tickerCellHtml = isNameFirst()
        ? '<span class="tkr-name">' + r.name + '</span><span class="tkr">' + r.ticker + '</span>'
        : '<span class="tkr">' + r.ticker + '</span><span class="tkr-name">' + r.name + '</span>';
      return '<td class="col-ticker' + (isNameFirst() ? ' name-first' : '') + '">' + tickerCellHtml + '</td>' +
        '<td class="left group-start"><span class="verdict v-' + r.tier + '">' + TIER_LABEL[r.tier] + '</span></td>' +
        '<td>' + scoreCell + '</td>' +
        '<td>' + factorsCell + '</td>';
    }

    function rowHtml(r) { return isEtf() ? rowHtmlEtf(r) : rowHtmlStock(r); }

    function rowHtmlEtf(r) {
      var d = r.d;
      var rangeTitle = (isNum(d.wk52Low) && isNum(d.wk52High))
        ? '52-week range: ' + fmtPrice(d.wk52Low) + ' to ' + fmtPrice(d.wk52High) : '';
      return '<tr data-ticker="' + r.ticker + '">' +
        screenCells(r) +
        '<td class="grp-snapshot group-start">' + fmtMoney(r.aum) + '</td>' +
        '<td class="grp-snapshot">' + fmtPrice(r.price) + '</td>' +
        '<td class="grp-snapshot ' + clsChange(r.changePct) + '">' + fmtChange(r.changePct) + '</td>' +
        '<td class="grp-performance group-start ' + colorFromPts(r.parts.ytd) + '">' + fmtRet(r.ytd) + '</td>' +
        '<td class="grp-performance ' + colorScored(r.parts.ret1y) + '">' + fmtRet(r.ret1y) + '</td>' +
        '<td class="grp-performance ' + colorScored(r.parts.ret5y) + '">' + fmtRet(r.ret5y) + '</td>' +
        '<td class="grp-performance ' + colorScored(r.parts.ret10y) + '">' + fmtRet(r.ret10y) + '</td>' +
        '<td class="grp-income group-start ' + colorFromPts(r.parts.yieldPct) + '">' + fmtPct2(r.yieldPct) + '</td>' +
        '<td class="grp-income ' + colorFromPts(r.parts.expenseRatio) + '">' + fmtPct2(r.expenseRatio) + '</td>' +
        '<td class="grp-income ' + colorFromPts(r.parts.netYield) + '">' + fmtPct2(r.netYield) + '</td>' +
        '<td class="grp-technicals group-start ' + colorScored(r.parts.rsi) + '">' + fmtRsi(r.rsi) + '</td>' +
        '<td class="grp-technicals ' + colorScored(r.parts.wk52) + '" title="' + rangeTitle + '">' + fmtRangePos(r.wk52) + '</td>' +
        '<td class="grp-technicals ' + colorFromPts(r.parts.pctVs20dma) + '">' + fmtRet(r.pctVs20dma) + '</td>' +
        '<td class="grp-technicals ' + colorFromPts(r.parts.pctVs100dma) + '">' + fmtRet(r.pctVs100dma) + '</td>' +
        '<td class="grp-technicals ' + colorScored(r.parts.pctVs200dma) + '">' + fmtRet(r.pctVs200dma) + '</td>' +
        '<td class="grp-snapshot group-start ' + clsAge(r.updated) + '" title="' + ageTitle(d) + '">' + fmtAge(r.updated) + '</td>' +
        '</tr>';
    }

    function rowHtmlStock(r) {
      var d = r.d;
      return '<tr data-ticker="' + r.ticker + '">' +
        screenCells(r) +
        '<td class="grp-snapshot group-start">' + fmtMoney(r.marketCap, r.cur) + '</td>' +
        '<td class="grp-snapshot">' + fmtPrice(r.price, r.cur) + '</td>' +
        '<td class="grp-snapshot ' + clsChange(r.changePct) + '">' + fmtChange(r.changePct) + '</td>' +
        '<td class="grp-growth group-start ' + colorScored(r.parts.revTTM) + '">' + fmtPct(r.revTTM) + '</td>' +
        '<td class="grp-growth ' + colorScored(r.parts.revFwd) + '">' + fmtPct(r.revFwd) + '</td>' +
        '<td class="grp-growth ' + colorScored(r.parts.epsTTM) + '">' + fmtPct(r.epsTTM) + '</td>' +
        '<td class="grp-growth ' + colorScored(r.parts.epsFwd) + '">' + fmtPct(r.epsFwd) + '</td>' +
        '<td class="grp-valuation group-start ' + colorFromPts(r.parts.peVsG) + '">' + fmtNum(r.peFwd) + '</td>' +
        '<td class="grp-valuation ' + colorScored(r.parts.pegFwd) + '">' + fmtNum(r.pegFwd) + '</td>' +
        '<td class="grp-balance group-start ' + colorScored(r.parts.cashDebt) + '">' + fmtMoney(r.cash, r.cur) + '</td>' +
        '<td class="grp-balance">' + fmtMoney(r.debt, r.cur) + '</td>' +
        '<td class="grp-balance ' + colorScored(r.parts.cashDebt) + '">' + fmtRatio(r.cashDebt) + '</td>' +
        '<td class="grp-balance ' + colorFromPts(r.parts.netCashMc) + '">' + fmtPct(r.netCashMc) + '</td>' +
        '<td class="grp-snapshot group-start ' + clsAge(r.updated) + '" title="' + ageTitle(d) + '">' + fmtAge(r.updated) + '</td>' +
        '</tr>';
    }

    function updateSortIndicators() {
      var ths = document.querySelectorAll("tr.head-row th");
      ths.forEach(function (th) {
        var k = th.getAttribute("data-sort");
        var existing = th.querySelector(".arrow");
        if (existing) existing.remove();
        if (k === sortKey) {
          var span = document.createElement("span");
          span.className = "arrow";
          span.textContent = sortDir === -1 ? "▼" : "▲";
          th.appendChild(span);
        }
      });
    }

    // ---- Column visibility ----
    function applyColumnVisibility() {
      COL_GROUPS[modeKind()].forEach(function (g) {
        var cb = document.querySelector('#colsMenu input[data-group="' + g[0] + '"]');
        var show = cb ? cb.checked : true;
        document.querySelectorAll(".grp-" + g[0]).forEach(function (el) {
          el.classList.toggle("col-hidden", !show);
        });
      });
    }

    // ---- Responsive auto-hide (v4.0.0) ----
    // Least decision-relevant groups drop first so a narrow window never
    // needs horizontal scroll: Ticker/Tier/Score/Factors (outside COL_GROUPS,
    // always visible) plus as many groups as fit. Order is a judgment call --
    // context-only columns before either scored pillar, and between the two
    // scored pillars the heavier-weighted one (stock Growth: 60 of 100; ETF
    // Technicals and Performance are tied at 50/50 so Technicals -- the
    // entry-timing half -- stays a beat longer since it changes day to day).
    var HIDE_ORDER = {
      stock: ["snapshot", "balance", "valuation", "growth"],
      etf: ["income", "snapshot", "performance", "technicals"]
    };
    var WIDTH_TIERS = [1440, 1150, 900, 700]; // px; below tier[i] hide HIDE_ORDER[0..i]

    function autoHiddenCount(width) {
      var n = 0;
      for (var i = 0; i < WIDTH_TIERS.length; i++) {
        if (width < WIDTH_TIERS[i]) n++;
      }
      return n;
    }

    // Live-responsive: recomputed on every resize, overriding any manual
    // Columns-menu picks until the next breakpoint crossing (owner decision,
    // 2026-07-04) -- the v4.0.0 goal is that scrolling is never required at
    // any width, which a "sticky until universe change" default can't guarantee.
    function applyResponsiveColumns() {
      var kind = modeKind();
      var order = HIDE_ORDER[kind];
      var hideCount = Math.min(autoHiddenCount(window.innerWidth), order.length);
      var hidden = order.slice(0, hideCount);
      COL_GROUPS[kind].forEach(function (g) {
        var cb = document.querySelector('#colsMenu input[data-group="' + g[0] + '"]');
        if (cb) cb.checked = hidden.indexOf(g[0]) === -1;
      });
      applyColumnVisibility();
    }

    var responsiveResizeTimer = null;
    function scheduleResponsiveColumns() {
      clearTimeout(responsiveResizeTimer);
      responsiveResizeTimer = setTimeout(applyResponsiveColumns, 120);
    }

    // ---- Per-stock breakdown popup ----
    var POPUP_METRICS = [
      { key: "revTTM",      label: "Revenue Growth TTM", weight: 10, fmt: function (d) { return fmtPct(d.revTTM); } },
      { key: "epsTTM",      label: "EPS Growth TTM",     weight: 15, fmt: function (d) { return fmtPct(d.epsTTM); } },
      { key: "revFwd",      label: "Revenue Growth FWD", weight: 10, fmt: function (d) { return fmtPct(d.revFwd); } },
      { key: "epsFwd",      label: "EPS Growth FWD",     weight: 15, fmt: function (d) { return fmtPct(d.epsFwd); } },
      { key: "pegFwd",      label: "PEG FWD",            weight: 25, fmt: function (d) { return fmtNum(pegDisplay(d)); } },
      { key: "cashDebt",    label: "Cash vs Debt",       weight: 25, fmt: function (d) { return fmtRatio(cashDebtRatio(d)); } }
    ];

    var ETF_POPUP_METRICS = [
      { key: "rsi",          label: "RSI (14-day)",           weight: 20, fmt: function (d) { return fmtRsi(d.rsi); } },
      { key: "wk52",         label: "52-Week Range position", weight: 20, fmt: function (d) { return fmtRangePos(wk52Pos(d)); } },
      { key: "ret1y",        label: "1 Year Total Return",    weight: 10, fmt: function (d) { return fmtRet(d.ret1y); } },
      { key: "ret5y",        label: "5 Year Total Return",    weight: 20, fmt: function (d) { return fmtRet(d.ret5y); } },
      { key: "ret10y",       label: "10 Year Total Return",   weight: 20, fmt: function (d) { return fmtRet(d.ret10y); } },
      { key: "pctVs200dma",  label: "Price vs 200-Day MA",    weight: 10, fmt: function (d) { return fmtRet(d.pctVs200dma); } }
    ];

    function ordinal(p) {
      if (p === undefined || p === null) return "—";
      var n = Math.round(p * 100);
      var s = (n % 10 === 1 && n % 100 !== 11) ? "st" : (n % 10 === 2 && n % 100 !== 12) ? "nd" : (n % 10 === 3 && n % 100 !== 13) ? "rd" : "th";
      return n + s;
    }

    function openStock(ticker) {
      var d = data[ticker];
      if (!d || !Object.keys(d).length) return;
      var nm = (data[ticker] && data[ticker].name) || ticker;
      var sm = computeScoreMap();
      var sc = sm[ticker] || { pct: null, parts: {}, pctiles: {}, total: 0 };
      var tier = sc.pct === null ? "none" : computeTierMap(sm)[ticker];
      var tlabel = tier === "none" ? "NO DATA" : "Tier " + TIER_LABEL[tier];

      // International leads the popup with the company name too, matching the
      // table row; every other universe keeps the ticker as the title.
      $("stockTitle").textContent = isNameFirst() ? nm : ticker;
      $("stockSub").innerHTML = (isNameFirst() ? ticker : nm) + ' &middot; <span class="verdict v-' + tier + '">' + tlabel +
        '</span> &middot; Score ' + (sc.pct === null ? "—" : sc.pct) + "/100";

      $("stockRows").innerHTML = (isEtf() ? ETF_POPUP_METRICS : POPUP_METRICS).map(function (m) {
        var pp = sc.parts[m.key];
        var color = colorScored(pp);
        var ptsTxt = (pp === undefined || pp === null)
          ? "0.0/" + m.weight                              // missing data = hard zero
          : (pp / 20 * m.weight).toFixed(1) + "/" + m.weight;
        return "<tr>" +
          "<td>" + m.label + "</td>" +
          '<td class="num ' + color + '">' + m.fmt(d) + "</td>" +
          '<td class="num">' + ordinal(sc.pctiles[m.key]) + "</td>" +
          '<td class="num ' + color + '">' + ptsTxt + "</td>" +
          "</tr>";
      }).join("");

      $("stockNote").innerHTML = isEtf()
        ? "Each metric's points come from its rank among the 10 funds (best = full points, worst = 0, " +
          "evenly spaced, ties averaged), weighted by pillar: Technicals 50, Performance 50 " +
          "(5-year and 10-year returns count double the 1-year return). A missing metric (—) scores zero. Open <b>Methodology</b> for the full method."
        : "Each metric's points come from its percentile rank vs the " +
          UNIVERSES[universeMode].label + " (green = top of the pack, red = bottom), weighted by pillar: " +
          "TTM 25, FWD 25, Valuation 25, Balance sheet 25. A missing metric (—) scores zero. " +
          "Open <b>Methodology</b> for the full method.";

      $("stockModal").hidden = false;
    }
    function closeStock() { $("stockModal").hidden = true; }

    // ---- Modals ----
    // The methodology popup carries one section per model; show the one that
    // matches the active universe kind.
    function openMethodology() {
      var etf = isEtf();
      $("methodStock").hidden = etf;
      $("methodEtf").hidden = !etf;
      $("methodologyModal").hidden = false;
    }
    function closeMethodology() { $("methodologyModal").hidden = true; }

    // ---- Events ----
    function bind() {
      // tier filter chips
      document.querySelectorAll(".chip").forEach(function (c) {
        c.addEventListener("click", function () {
          document.querySelectorAll(".chip").forEach(function (x) { x.classList.remove("active"); });
          c.classList.add("active");
          filter = c.getAttribute("data-filter");
          render();
        });
      });

      // sort (delegated: the ETF universe re-renders the <thead>)
      document.querySelector("#table thead").addEventListener("click", function (e) {
        var th = e.target.closest("th");
        if (!th) return;
        var k = th.getAttribute("data-sort");
        if (!k) return;
        if (sortKey === k) { sortDir = -sortDir; }
        else { sortKey = k; sortDir = (k === "ticker") ? 1 : -1; }
        render();
      });

      // search
      $("search").addEventListener("input", function () { query = this.value.trim(); render(); });

      // row click -> per-stock breakdown
      tbody.addEventListener("click", function (e) {
        var tr = e.target.closest("tr");
        if (tr && tr.dataset.ticker) openStock(tr.dataset.ticker);
      });

      // columns menu
      $("colsBtn").addEventListener("click", function (e) {
        e.stopPropagation();
        $("colsMenu").hidden = !$("colsMenu").hidden;
      });
      document.addEventListener("click", function () { $("colsMenu").hidden = true; });
      $("colsMenu").addEventListener("click", function (e) { e.stopPropagation(); });
      // delegated: the ETF universe re-renders the menu's checkboxes
      $("colsMenu").addEventListener("change", applyColumnVisibility);

      // universe buttons (Nasdaq 100 / S&P 500 / Growth / Value / Dividend)
      document.querySelectorAll("#universeGroup .u-btn").forEach(function (b) {
        b.addEventListener("click", function () {
          var target = b.getAttribute("data-universe");
          // Manually switching to a different universe drops the MAG 10 filter --
          // it's meaningfully tied to S&P 500 data specifically, not a general toggle.
          if (mag10Active && target !== "sp500") { mag10Active = false; updateMag10Button(); }
          selectUniverse(target);
        });
      });

      // MAG 10 watchlist toggle
      $("mag10Btn").addEventListener("click", toggleMag10);

      // Responsive column auto-hide (v4.0.0): re-evaluate on resize so no
      // width ever needs a horizontal scrollbar to see Ticker/Tier/Score.
      window.addEventListener("resize", scheduleResponsiveColumns);

      // modals
      $("methodologyBtn").addEventListener("click", openMethodology);
      $("methodologyClose").addEventListener("click", closeMethodology);
      $("methodologyModal").addEventListener("click", function (e) { if (e.target === $("methodologyModal")) closeMethodology(); });
      $("stockClose").addEventListener("click", closeStock);
      $("stockModal").addEventListener("click", function (e) { if (e.target === $("stockModal")) closeStock(); });

      document.addEventListener("keydown", function (e) { if (e.key === "Escape") { closeMethodology(); closeStock(); } });
    }

    // ---- Init ----
    loadState();
    bind();
    applyResponsiveColumns();
    render();
    loadInitial();
  })();
