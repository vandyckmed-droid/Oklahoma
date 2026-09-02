# Oklahoma

A U.S. equity universe: the current **S&P 500 membership**, pulled from
Financial Modeling Prep, enriched with live quotes and a year of adjusted
price history, with a phone-first page for inspecting it — live at
**<https://vandyckmed-droid.github.io/Oklahoma/web/>** (GitHub Pages serves
`main`, so every merged refresh updates the page).

Defining the universe as the index delegates membership to S&P's committee,
whose entry/exit buffer rules provide turnover hysteresis for free — no
selection logic of our own to flap names in and out on market noise. The
daily refresh simply mirrors whatever the index currently holds.

## Layout

```
oklahoma/config.py     universe source, history window, page settings
oklahoma/fmp.py        Financial Modeling Prep client, standard library only
oklahoma/universe.py   build / rank / save / load
oklahoma/history.py    end-of-day adjusted price history
oklahoma/metrics.py    calculations over the history (cumulative returns)
oklahoma/ui.py         renders the universe into a self-contained page
oklahoma/__main__.py   the CLI
data/universe.json     the committed universe
data/changes.json      append-only membership change log
data/history/          one price file per ticker, plus index.json
web/template.html      page source, a complete HTML document with two
                       JSON placeholders
web/index.html         generated standalone page — open it in a browser
tests/                 offline tests; no network, no API key
```

No third-party dependencies. Python 3.10+ (CI runs 3.10 and 3.13).

## Usage

The FMP key is read from `FMP_API_KEY`, falling back to `API_KEY`. It is never
written to disk or into any generated file.

```bash
export FMP_API_KEY=...

python -m oklahoma refresh     # pull from FMP, rewrite data/universe.json + web/index.html
python -m oklahoma history     # pull price history for every name in the universe
python -m oklahoma show        # print the universe, sectors and history coverage
python -m oklahoma build-ui    # regenerate web/index.html from the saved data
python -m oklahoma export-csv      # ticker,date,adj_close rows on stdout
python -m oklahoma export-returns  # ticker,date,cum_return_pct rows on stdout
```

Then open `web/index.html` — it is one self-contained file with the data
inlined, so it works from disk, from a static host, or over `python -m
http.server`.

## The data

Each constituent carries at least the three required fields — `ticker`,
`name`, `sector` — plus context that makes the row useful on its own:

```json
{
  "rank": 3,
  "ticker": "GOOGL",
  "name": "Alphabet Inc.",
  "sector": "Communication Services",
  "industry": "Internet Content & Information",
  "exchange": "NASDAQ",
  "market_cap": 4107206361600,
  "price": 339.19,
  "avg_volume": 30159865,
  "share_classes": ["GOOG", "GOOGL"]
}
```

The file itself records `schema_version`, `generated_at`, the `source`, and the
`criteria` the build ran under, so a universe file explains how it was made.

### Identity

Every row carries the company's **CIK** — the SEC's durable identifier — so
a ticker rename (FB becoming META) can never sever a company from its own
history. `date_first_added` records when the index admitted the name.

The index itself lists some companies twice (GOOG and GOOGL, FOX and FOXA);
mirroring it keeps both. `--collapse-share-classes` opts into one row per
company instead, grouped by CIK and keeping the most traded class.

## Price history

`python -m oklahoma history` pulls end-of-day bars for every name in the
universe and writes one file per ticker under `data/history/`, plus an
`index.json` recording what each ticker actually covers.

**`adj_close` is the canonical series.** It comes from FMP's
`historical-price-eod/dividend-adjusted` endpoint and is corrected for both
splits and dividends, so returns computed across it are comparable over
time. The plain `historical-price-eod/full` endpoint carries no adjusted
column at all, which is why it isn't used.

Each file is a flat, sorted series:

```json
{
  "schema_version": 1,
  "ticker": "AAPL",
  "price_field": "adj_close",
  "count": 301,
  "bars": [
    { "date": "2025-06-20", "adj_close": 200.03, "volume": 96813542 }
  ]
}
```

Bars are chronological, de-duplicated, and every one carries a date and an
adjusted close. Files are written **one bar per line**, so a daily refresh
shows up in review as the bar it appended rather than an opaque rewrite of
a single 20 KB line. Repository size is unaffected — git's delta
compression is byte-oriented and packs both layouts identically — but a
diff you can read is a correction you can catch. `export-csv` derives the
long `ticker,date,adj_close` format from these files on demand, so there
is no second copy to drift.

### Coverage

The target is `TRADING_DAYS_TARGET` (252) sessions per name. Markets trade
about 252 of 365 days, so the build requests a wider calendar window —
`calendar_days_for()` — and takes what comes back. In practice that yields
~300 trading days per name.

A name can legitimately fall short: a spinoff the committee admits soon
after listing has no year of history to fetch. Those names are kept in the
universe (membership is the index's call, not data availability's), marked
`"sufficient": false` in the index, and flagged in the UI rather than
silently dropped. `show` lists them.

Change the window with `--trading-days N` or `HISTORY_TRADING_DAYS`.

One file per ticker is what makes this expandable: growing the universe adds
files instead of rewriting one large one, and a single failed symbol never
corrupts the rest — failures are collected in the index, not raised.

## Calculations

`oklahoma/metrics.py` holds calculations over the stored history. It reads
and computes; it never fetches or stores, so derived numbers are recomputed
from `data/history/` on demand and there is no second copy to drift.

**Log trend.** A least-squares line through ln(adjusted close) over the
12-month window. On a log scale steady compounding is a straight line, so
the slope reads as the steady growth rate the year implies (shown
annualized) and R² measures how much of the year's path that one trend
explains. **Quality momentum** damps the trend by its reliability —
`trend %/yr × R²` — the classic quality-adjusted momentum score, and a
sort key on the page. The fitted line can be overlaid on each name's
chart; it renders gently curved there because the chart's axis is linear
while the fit is straight in log space.

Every figure on the page is **tap-to-explain**: underlined labels open a
sheet with a plain-language sentence and the formula, instead of fine
print scattered through the layout.

Return windows come in four lengths — **12-month** (252 sessions),
**6-month** (126), **3-month** (63) and **1-month** (21) — each measured from the first close
of its own window. A name that cannot fill a window gets no figure for it
rather than a shorter one wearing the same label; the page shows a dash
and sinks the name under that sort.

The other headline metric is **daily cumulative return over the 12-month window**:
each day's total return since the window's first close, starting at 0%.
`export-returns` emits the full daily series; the page computes its thinned
copy per name at build time and shows each name's series against a 0%
baseline. A name with less than a full year of history is measured over
what it has, with `window_trading_days` recording the span.

The history index (`data/history/index.json`) is deliberately a coverage
manifest only — ticker, span, and whether it suffices. Anything derivable
(returns, ranges, display series) is recomputed from the bar files when the
page is built, so the index can never disagree with the data it points at.

### Cross-section

The page opens with a 12-month cross-section computed at build time from
the same returns: per-sector **median return** and **breadth** (the share
of names positive — the guard that keeps a three-winner sector from
looking healthy on its median alone), plus the window's five leaders and
laggards, tappable to jump to the name. Only names covering the full
window participate; mixing a 55-day return into 252-day medians would
quietly corrupt the comparison.

## Automated refresh

`.github/workflows/refresh.yml` refreshes the dataset every weekday evening
(01:30 UTC Tue-Sat, after each U.S. session) and can be run by hand from the
Actions tab. It pulls the universe and history, runs the offline test suite
against the freshly written files — so bad data from the API fails the run
instead of landing on `main` — and commits the result directly to `main`
only when something changed.

It needs one repository secret: **`FMP_API_KEY`** (Settings → Secrets and
variables → Actions). Until the secret exists, scheduled runs fail at the
fetch step and the data simply stays at its last committed state.

## Changing the universe

The universe is whatever `UniverseConfig.source` names — today that is the
S&P 500 constituents endpoint. A different index (or a screener-based rule)
is a new fetch function plus a config value; everything downstream keys off
the constituent list. `--size N` (or `UNIVERSE_SIZE`) keeps only the largest
N names when a smaller universe is useful for experiments.

When a name leaves the index, the next `history` run prunes its price file,
so departures do not accumulate as orphans.

### Membership changes

Each `refresh` compares the new membership against the previous one — by
CIK, so a ticker rename registers as a rename, never as one company
leaving and a stranger arriving — and appends any difference to
`data/changes.json`:

```json
{
  "observed_at": "2026-09-02T01:30:00Z",
  "joined": [{ "ticker": "RDDT", "name": "Reddit, Inc.", "cik": "0001713445" }],
  "left": [],
  "renamed": []
}
```

The log is append-only: each entry is a committee decision observed at a
refresh, which is exactly the record a current-state snapshot cannot
reconstruct later. The page shows the most recent events.

### Staleness

The page compares its embedded timestamp against the viewer's clock and
shows a warning banner when the data is more than five days old (long
weekends stay quiet), so a silently failing refresh looks broken instead
of current.

## The page

The page is built around three questions: which names are worth a look
(cross-section, sort, filters), why a given name is interesting (per-name
detail: return vs its sector's median, distance from its 1-year high, the
cumulative-return chart with its trend line), and whether it adds something
the shortlist doesn't already have (the watchlist).

The page is a tabbed app with a bottom tab bar: **Universe** (masthead,
search, sector chips, the list), **Sectors** (the 12-month cross-section),
**Watchlist** (the starred names in the same view, with copy/paste tools)
and **Settings** (every control in one place: view, the figure shown on
cards, sort and direction, group by sector, the column explainer, and the
data notes). Tapping a table heading still sorts in place, since that is
an act on the data rather than a setting; the Settings sort mirrors it.
The stale-data warning stays a banner on every tab.

One **metric registry** in the template drives every surface, so a figure
means the same thing wherever it appears. The list has two views. **Cards**
show each name as a sparkline plus one labeled figure chosen from the Show
menu (12-mo, 6-mo, 3-mo, 1-mo, off high, vs sector, trend, R², quality,
last close). **Table** is built for density on a phone: ticker only,
three-letter sector codes, one-decimal figures, and every column at once.
It scrolls sideways inside its own region so the header row and the
ticker column stay put, and tapping a column heading sorts by it (again
to flip). Tapping any name
in either view opens the same detail as a bottom sheet. The chosen view,
figure and sort are remembered per device.

The **watchlist** is stored in the browser (`localStorage`) — a personal
shortlist on that device, not synced state. Starred names show a marker in
the list, the Watchlist tab shows only them, and each name's detail
notes how much of the current watchlist already sits in the same sector.

## Tests and CI

```bash
python -m unittest discover -s tests
```

The tests run offline against fixtures — **no network and no API key** — so
CI verifies the core system on every pull request without secrets.
`.github/workflows/ci.yml` runs the suite on Python 3.10 and 3.13, and
separately rebuilds `web/index.html` from the committed data to prove the
generated page has not drifted from the data it claims to show.

Beyond the fixtures, the suite asserts invariants on the committed data:

- **Universe** — every name has a ticker, a company name and a sector;
  tickers are unique; ranks are dense; market caps descend.
- **History** — every universe name has a history file; bars are
  chronological, de-duplicated and positively priced; each file's count
  matches the index; nothing failed to load; `adj_close` is the canonical
  field; and all but at most two names cover the full window, so a
  widespread shortfall fails the build instead of passing quietly.
