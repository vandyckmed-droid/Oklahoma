# Oklahoma

A U.S. equity universe: the largest listed companies by market capitalization,
pulled from Financial Modeling Prep and kept as a small, versioned JSON file
with a phone-first page for inspecting it.

The universe currently holds the **top 50** names. Nothing in the code is
pinned to 50 — see [Growing the universe](#growing-the-universe).

## Layout

```
oklahoma/config.py     selection rules (size, exchanges, market-cap ladder)
oklahoma/fmp.py        Financial Modeling Prep client, standard library only
oklahoma/universe.py   build / rank / save / load
oklahoma/ui.py         renders the universe into a self-contained page
oklahoma/__main__.py   the CLI
data/universe.json     the committed universe
web/template.html      page source (fragment: title, styles, markup, script)
web/index.html         generated standalone page — open it in a browser
tests/                 offline tests; no network, no API key
```

No third-party dependencies. Python 3.9+.

## Usage

The FMP key is read from `FMP_API_KEY`, falling back to `API_KEY`. It is never
written to disk or into any generated file.

```bash
export FMP_API_KEY=...

python -m oklahoma refresh     # pull from FMP, rewrite data/universe.json + web/index.html
python -m oklahoma show        # print the universe and its sector breakdown
python -m oklahoma build-ui    # regenerate web/index.html from the saved data
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

### Selection rules

- **Common stock only.** ETFs, funds, and inactive listings are excluded at
  the screener.
- **Primary U.S. line only.** Foreign cross-listings of the same company
  (`NVDA.NE`) are dropped; they are the same company on a different exchange.
- **One row per company.** Berkshire's A and B shares are one company that
  would otherwise take two universe slots. The most liquid class is kept and
  the others are recorded in `share_classes`. Pass
  `--keep-all-share-classes` to give each class its own slot instead.

## Growing the universe

Size is a parameter, not a constant. Three ways to change it:

```bash
python -m oklahoma refresh --size 250   # one-off
UNIVERSE_SIZE=250 python -m oklahoma refresh
```

...or change the default in `oklahoma/config.py`.

The screener needs a market-cap floor to page against, and a floor that suits
50 names is far too high for 500. `MARKET_CAP_FLOORS` in `config.py` is a
descending ladder; the build walks down it until the candidate pool is
comfortably larger than the target, so a bigger universe needs no other
change. `UNIVERSE_EXCHANGES` (or `config.exchanges`) widens the venue list the
same way.

## Tests

```bash
python -m unittest discover -s tests
```

The tests run offline against fixtures, and additionally assert invariants on
the committed `data/universe.json`: every name has a ticker, a company name
and a sector; tickers are unique; ranks are dense; market caps descend.
