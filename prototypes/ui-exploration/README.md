# Rapid UI exploration — nine mobile directions

**Saved for later.** The live, operable gallery of all nine is published at
https://claude.ai/code/artifact/fb0404d7-d6c3-467d-8e70-4302e3cb68fd — open it on a
phone to try each direction. This folder is its source.

Disposable design instruments, not implementation candidates. Open
`index.html` for the gallery: nine live, operable phone previews side by
side, each with its thesis, its strongest advantage and its principal
tradeoff.

Directions 1–8 each commit to a single thesis. Direction 9 is the
synthesis of 5, 6, 7 and 8 — the combination worth pursuing if any of this
goes further.

**Production is untouched.** Nothing in `web/`, `oklahoma/`, `data/` or
`worker/` was modified. These files are additive and self-contained.

## The directions

| # | Name | Thesis |
|---|------|--------|
| 1 | **Ledger** | The universe as a printed market page — serif, hairline rules, no coloured pills. |
| 2 | **Terminal** | Every number on screen at once, filtered by expressions (`r2>0.85 r12>40`). |
| 3 | **Deck** | Screening is triage, so names are dealt one card at a time. |
| 4 | **Heatmap** | The market's shape before its list — a treemap sized by cap, coloured by any metric. |
| 5 | **Brief** | The app answers the questions; the ranked list is an appendix. |
| 6 | **Dial** | Position over ranking — two pickable axes, named quadrants, drag to select. |
| 7 | **Focus** | Your twelve names, at a size readable without glasses. |
| 8 | **Strata** | Browse by sector structure; compare by collecting names into an overlay tray. |
| 9 | **Hybrid** | The synthesis: Focus as home, Brief's answers as the market view, Dial as the explorer, and Strata's tray reachable from every list. |

### What the hybrid actually combines

Three tabs and one persistent tray:

- **Yours** — the watchlist at Focus's size and quiet, with a window lens
  and a full-page detail view.
- **Market** — Brief's answered questions over their evidence, then the
  sector list. Tapping a sector hands off into Explore with that sector
  isolated, so structure leads somewhere instead of dead-ending.
- **Find** — search across all 503, or Explore: Dial's two-axis plot with
  named quadrants and drag-to-select.
- **Compare tray** — Strata's overlay, but not a screen. Every list in the
  app carries a per-row `⊕`, so putting two names on one re-based chart
  never requires navigating anywhere.

The point of the synthesis is that comparison stops being a place you go.

## How to look at them

Any static server, or just open the files — they are plain HTML with no
build step, no network calls and no dependencies.

```
python3 -m http.server 8000 --directory prototypes/ui-exploration
# then http://localhost:8000/
```

Each prototype also stands alone: `01-ledger.html`, `02-terminal.html`, and
so on. All nine were designed and verified at 390 × 844.

## The data

`data.js` is a shared fixture extracted **verbatim** from the production
build (`web/index.html`) — real tickers, company names, sectors,
industries, market caps, adjusted closes, and every derived metric the
production page computes: 1/3/6/12-month returns, 12-1 and 6-1 momentum,
off-high, 52-week range, log-trend slope, R² and quality momentum, plus the
sector cross-section (medians, breadth, leaders, laggards). The only change
is that the cumulative-return sparklines are thinned from 60 points to 32.
Nothing in it is invented.

`kit.js` holds formatting, sorting and SVG path geometry only. No visual
opinion is shared between directions — each one styles from scratch.

Watchlists are per-prototype `localStorage` keys, so the directions never
collide with each other or with the production page's `oklahoma-watchlist`.

## Regenerating the fixture

After a data refresh, re-extract from the rebuilt page:

```python
# python3 - <<'PY'  (run from the repository root)
import re, json

src = open("web/index.html", encoding="utf-8").read()

def block(name):
    m = re.search(r'<script id="%s" type="application/json">(.*?)</script>' % name, src, re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))

uni, hist = block("universe-data"), block("history-data")
cov = {c["ticker"]: c for c in hist["coverage"]}

def thin(v, n):
    if not v or len(v) <= n:
        return v
    step = (len(v) - 1) / (n - 1)
    return [v[round(i * step)] for i in range(n)]

names = []
for r in uni["constituents"]:
    c = cov.get(r["ticker"], {})
    rec = {"t": r["ticker"], "n": r["name"], "s": r["sector"], "i": r.get("industry") or "",
           "cap": r["market_cap"], "px": c.get("last_adj_close", r.get("price")),
           "rank": r["rank"], "ok": bool(c.get("sufficient")), "days": c.get("trading_days"),
           "r12": c.get("window_return_pct"), "r6": c.get("return_6m_pct"),
           "r3": c.get("return_3m_pct"), "r1": c.get("return_1m_pct"),
           "m121": c.get("mom_12_1_pct"), "m61": c.get("mom_6_1_pct"),
           "lo": c.get("window_low"), "hi": c.get("window_high"),
           "trend": c.get("trend_ann_pct"), "r2": c.get("trend_r2"), "qual": c.get("quality_pct"),
           "sp": [round(v, 1) for v in thin(c.get("cum_return_spark") or [], 32)],
           "fit": [round(v, 1) for v in thin(c.get("fit_spark") or [], 32)]}
    if rec["hi"] and rec["px"]:
        rec["off"] = round((rec["px"] / rec["hi"] - 1) * 100, 1)
    names.append(rec)

payload = {"generated_at": hist["generated_at"],
           "as_of": max(c["end_date"] for c in hist["coverage"]),
           "window_start": min((c.get("window_start_date") or c["start_date"])
                               for c in hist["coverage"]),
           "count": len(names), "sufficient": hist["sufficient_count"],
           "sectors": hist["cross_section"]["sectors"],
           "leaders": hist["cross_section"]["leaders"],
           "laggards": hist["cross_section"]["laggards"], "names": names}

with open("prototypes/ui-exploration/data.js", "w", encoding="utf-8") as fh:
    fh.write("window.OK = " + json.dumps(payload, separators=(",", ":")) + ";\n")
# PY
```

## What these are not

No production architecture, no reusable abstractions, no backend, no error
handling, no tests, no build. Prototyping here was allowed every
implementation shortcut and no design shortcuts. Choosing a direction is a
separate decision; none of this is authorisation to ship one.
