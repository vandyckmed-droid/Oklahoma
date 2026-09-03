/* Style-neutral helpers shared by every prototype.
   Formatting and geometry only — no visual opinions live here, so each
   direction is free to look nothing like its neighbours. */
(function (global) {
  var OK = global.OK;
  var names = OK.names;

  var byTicker = {};
  names.forEach(function (r) { byTicker[r.t] = r; });

  /* ---- numbers ---- */
  function signed(v, d, suffix) {
    if (v == null) return "—";
    var s = Math.abs(v).toFixed(d) + (suffix || "");
    return v > 0 ? "+" + s : v < 0 ? "−" + s : s;
  }
  function pct(v, d) { return v == null ? "—" : signed(v, d == null ? 1 : d, "%"); }
  function money(v) {
    if (v == null) return "—";
    if (v >= 1e12) return "$" + (v / 1e12).toFixed(2) + "T";
    if (v >= 1e9) return "$" + (v / 1e9).toFixed(0) + "B";
    if (v >= 1e6) return "$" + (v / 1e6).toFixed(0) + "M";
    return "$" + Math.round(v).toLocaleString();
  }
  function price(v) {
    return v == null ? "—" : "$" + v.toLocaleString(undefined,
      { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  function dir(v) {
    if (v == null) return "flat";
    if (v > 0.005) return "up";
    if (v < -0.005) return "down";
    return "flat";
  }
  function median(vals) {
    var v = vals.filter(function (x) { return x != null; })
                .sort(function (a, b) { return a - b; });
    if (!v.length) return null;
    var m = v.length >> 1;
    return v.length % 2 ? v[m] : (v[m - 1] + v[m]) / 2;
  }

  /* ---- the metrics the production app exposes ---- */
  var METRICS = {
    cap:   { label: "Market cap",        short: "Cap",     neutral: true, get: function (r) { return r.cap; },   fmt: money },
    r12:   { label: "12-month return",   short: "12M",     get: function (r) { return r.r12; },   fmt: pct },
    r6:    { label: "6-month return",    short: "6M",      get: function (r) { return r.r6; },    fmt: pct },
    r3:    { label: "3-month return",    short: "3M",      get: function (r) { return r.r3; },    fmt: pct },
    r1:    { label: "1-month return",    short: "1M",      get: function (r) { return r.r1; },    fmt: pct },
    m121:  { label: "12-1 momentum",     short: "12-1",    get: function (r) { return r.m121; },  fmt: pct },
    m61:   { label: "6-1 momentum",      short: "6-1",     get: function (r) { return r.m61; },   fmt: pct },
    off:   { label: "Off 1-year high",   short: "Off high",get: function (r) { return r.off; },
             fmt: function (v) { return v == null ? "—" : v > -0.5 ? "At high" : signed(v, 1, "%"); } },
    vsmed: { label: "Vs sector median",  short: "Vs sector", get: function (r) {
               var m = medianBySector[r.s];
               return (m == null || r.r12 == null || !r.ok) ? null : r.r12 - m;
             }, fmt: function (v) { return v == null ? "—" : signed(v, 1, " pts"); } },
    trend: { label: "Trend (log slope)", short: "Trend",   get: function (r) { return r.trend; },
             fmt: function (v) { return v == null ? "—" : signed(v, 1, "%/yr"); } },
    r2:    { label: "R² of trend",  short: "R²", neutral: true, get: function (r) { return r.r2; },
             fmt: function (v) { return v == null ? "—" : v.toFixed(2); } },
    qual:  { label: "Quality momentum",  short: "Quality", get: function (r) { return r.qual; },
             fmt: function (v) { return v == null ? "—" : signed(v, 1, "%/yr"); } },
    px:    { label: "Last close",        short: "Last",    neutral: true, get: function (r) { return r.px; }, fmt: price }
  };
  var METRIC_ORDER = ["cap", "r12", "r6", "r3", "r1", "m121", "m61", "off", "vsmed", "trend", "r2", "qual", "px"];

  var medianBySector = {};
  (function () {
    var bucket = {};
    names.forEach(function (r) {
      if (!r.ok || r.r12 == null) return;
      (bucket[r.s] = bucket[r.s] || []).push(r.r12);
    });
    Object.keys(bucket).forEach(function (s) { medianBySector[s] = median(bucket[s]); });
  })();

  var sectorNames = OK.sectors.map(function (s) { return s.sector; });
  var sectorCount = {};
  names.forEach(function (r) { sectorCount[r.s] = (sectorCount[r.s] || 0) + 1; });

  /* One hue per sector, deliberately plain: each prototype restyles or
     ignores it. Ordered to keep neighbouring sectors distinguishable. */
  var SECTOR_HUE = {
    "Technology": 205, "Healthcare": 158, "Financial Services": 265,
    "Consumer Cyclical": 25, "Industrials": 42, "Communication Services": 320,
    "Consumer Defensive": 96, "Energy": 8, "Utilities": 185,
    "Real Estate": 292, "Basic Materials": 65, "Unclassified": 0
  };
  function hue(sector) { return SECTOR_HUE[sector] == null ? 0 : SECTOR_HUE[sector]; }
  var SECTOR_ABBR = {
    "Technology": "Tech", "Healthcare": "Health", "Financial Services": "Financials",
    "Consumer Cyclical": "Cons. Cyc.", "Industrials": "Industrials",
    "Communication Services": "Comms", "Consumer Defensive": "Cons. Def.",
    "Energy": "Energy", "Utilities": "Utilities", "Real Estate": "Real Estate",
    "Basic Materials": "Materials"
  };
  function abbr(s) { return SECTOR_ABBR[s] || s; }

  /* ---- window lenses, matching the production app ---- */
  var WINDOWS = [
    { key: "1M", label: "1 month",  points: 3,  field: "r1" },
    { key: "3M", label: "3 months", points: 8,  field: "r3" },
    { key: "6M", label: "6 months", points: 16, field: "r6" },
    { key: "1Y", label: "12 months", points: null, field: "r12" }
  ];
  function windowByKey(k) {
    for (var i = 0; i < WINDOWS.length; i++) if (WINDOWS[i].key === k) return WINDOWS[i];
    return WINDOWS[3];
  }
  /* A shorter window keeps the tail of the same cumulative series and
     re-bases it to zero at its own start — the production rule. */
  function rebase(series, points) {
    if (!series || !series.length) return [];
    if (!points || points >= series.length) return series.slice();
    var tail = series.slice(series.length - points), base = 1 + tail[0] / 100;
    return tail.map(function (v) { return ((1 + v / 100) / base - 1) * 100; });
  }

  /* ---- geometry ---- */
  /* An SVG path through a series, scaled into w x h. Returns the path and
     the scale so callers can add dots, fills or a zero line. */
  function pathFor(series, w, h, opts) {
    opts = opts || {};
    var pad = opts.pad == null ? 2 : opts.pad;
    var all = opts.with ? series.concat(opts.with) : series.slice();
    if (opts.zero) all.push(0);
    var lo = Math.min.apply(null, all), hi = Math.max.apply(null, all);
    var span = (hi - lo) || 1;
    function y(v) { return pad + (1 - (v - lo) / span) * (h - pad * 2); }
    function x(i, n) { return n < 2 ? 0 : (i / (n - 1)) * w; }
    function d(s) {
      return s.map(function (v, i) {
        return (i ? "L" : "M") + x(i, s.length).toFixed(1) + " " + y(v).toFixed(1);
      }).join(" ");
    }
    return {
      d: d(series), line: d, x: x, y: y, lo: lo, hi: hi,
      area: series.length < 2 ? "" :
        d(series) + " L" + w.toFixed(1) + " " + (h - pad).toFixed(1) + " L0 " + (h - pad).toFixed(1) + " Z"
    };
  }
  function spark(series, w, h, opts) {
    opts = opts || {};
    if (!series || series.length < 2) return "";
    var g = pathFor(series, w, h, opts);
    var out = '<svg viewBox="0 0 ' + w + ' ' + h + '" preserveAspectRatio="none" aria-hidden="true"' +
      (opts.cls ? ' class="' + opts.cls + '"' : "") + ' style="width:100%;height:100%;overflow:visible">';
    if (opts.fill) out += '<path d="' + g.area + '" fill="' + opts.fill + '" stroke="none"/>';
    out += '<path d="' + g.d + '" fill="none" stroke="' + (opts.stroke || "currentColor") +
      '" stroke-width="' + (opts.width || 1.5) + '" stroke-linejoin="round" stroke-linecap="round"' +
      (opts.dash ? ' stroke-dasharray="' + opts.dash + '"' : "") + ' vector-effect="non-scaling-stroke"/>';
    if (opts.dot) out += '<circle cx="' + w + '" cy="' + g.y(series[series.length - 1]).toFixed(1) +
      '" r="' + (opts.dot === true ? 2.4 : opts.dot) + '" fill="' + (opts.stroke || "currentColor") + '"/>';
    return out + "</svg>";
  }

  /* ---- sorting / filtering ---- */
  function sortBy(list, key, desc) {
    var m = METRICS[key], sign = desc === false ? 1 : -1;
    return list.slice().sort(function (a, b) {
      var va = m.get(a), vb = m.get(b);
      if (va == null && vb == null) return a.rank - b.rank;
      if (va == null) return 1;
      if (vb == null) return -1;
      return sign * (va - vb) || a.rank - b.rank;
    });
  }
  function search(list, q) {
    q = (q || "").trim().toLowerCase();
    if (!q) return list;
    return list.filter(function (r) {
      return r.t.toLowerCase().indexOf(q) !== -1 || r.n.toLowerCase().indexOf(q) !== -1 ||
             r.s.toLowerCase().indexOf(q) !== -1 || r.i.toLowerCase().indexOf(q) !== -1;
    });
  }

  /* ---- watchlist, per prototype so they never collide ---- */
  function watchlist(key) {
    var K = "okproto-watch-" + key, set;
    try { set = new Set(JSON.parse(localStorage.getItem(K) || "[]")); }
    catch (e) { set = new Set(); }
    if (!set.size) ["NVDA", "LLY", "COST", "XOM", "JPM"].forEach(function (t) {
      if (byTicker[t]) set.add(t);
    });
    function save() { try { localStorage.setItem(K, JSON.stringify(Array.from(set))); } catch (e) {} }
    return {
      has: function (t) { return set.has(t); },
      toggle: function (t) { set.has(t) ? set.delete(t) : set.add(t); save(); return set.has(t); },
      list: function () { return Array.from(set).map(function (t) { return byTicker[t]; }).filter(Boolean); },
      get size() { return set.size; }
    };
  }

  function asOf() {
    var d = new Date(OK.as_of + "T00:00:00");
    return isNaN(d) ? OK.as_of
      : d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }
  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
                    .replace(/"/g, "&quot;");
  }

  global.KIT = {
    OK: OK, names: names, byTicker: byTicker,
    signed: signed, pct: pct, money: money, price: price, dir: dir, median: median, esc: esc,
    METRICS: METRICS, METRIC_ORDER: METRIC_ORDER, medianBySector: medianBySector,
    sectors: OK.sectors, sectorNames: sectorNames, sectorCount: sectorCount,
    hue: hue, abbr: abbr,
    WINDOWS: WINDOWS, windowByKey: windowByKey, rebase: rebase,
    pathFor: pathFor, spark: spark, sortBy: sortBy, search: search,
    watchlist: watchlist, asOf: asOf
  };
})(window);
