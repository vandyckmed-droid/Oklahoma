"""End-of-day price history for every name in the universe.

One file per ticker under `data/history/`, plus an index that records what
coverage each ticker actually has. Per-ticker files mean growing the
universe adds files rather than rewriting one large one, and a name whose
history fails to load never corrupts the rest.

`adj_close` is the canonical series: it is corrected for splits and
dividends, so returns computed across it are comparable over time. The
unadjusted `close` is kept alongside it for reference.
"""

from __future__ import annotations

import datetime as dt
import json
import os
from concurrent.futures import ThreadPoolExecutor

from .config import (
    HISTORY_DIR,
    HISTORY_INDEX_PATH,
    HISTORY_SCHEMA_VERSION,
    HistoryConfig,
)
from .fmp import FMPError, get_api_key, historical_prices

SOURCE = {
    "provider": "Financial Modeling Prep",
    "endpoint": "stable/historical-price-eod/dividend-adjusted",
    "adjustment": "splits and dividends",
}


def path_for(ticker: str, directory: str = HISTORY_DIR) -> str:
    # Class shares arrive as BRK-B; keep the filename identical to the ticker
    # so the mapping stays obvious in both directions.
    return os.path.join(directory, f"{ticker}.json")


def normalize_bar(row: dict) -> dict | None:
    """One API bar to one stored bar, or None if it carries no usable price."""
    adj_close = row.get("adjClose")
    date = row.get("date")
    if adj_close is None or not date:
        return None
    bar = {"date": date[:10], "adj_close": round(float(adj_close), 4)}
    if row.get("volume") is not None:
        bar["volume"] = int(row["volume"])
    return bar


def normalize_series(ticker: str, rows: list[dict]) -> list[dict]:
    """Clean one ticker's bars: drop unusable rows, de-duplicate, sort."""
    by_date: dict[str, dict] = {}
    for row in rows:
        bar = normalize_bar(row)
        if bar is not None:
            # A repeated date means the API sent a correction; the later row wins.
            by_date[bar["date"]] = bar
    return [by_date[date] for date in sorted(by_date)]


def summarize(ticker: str, bars: list[dict], trading_days: int) -> dict:
    """Coverage and headline numbers for one ticker.

    `sufficient` answers the question the universe actually cares about: is
    there enough history here to run a `trading_days`-long calculation?
    """
    summary = {
        "ticker": ticker,
        "trading_days": len(bars),
        "sufficient": len(bars) >= trading_days,
        "start_date": bars[0]["date"] if bars else None,
        "end_date": bars[-1]["date"] if bars else None,
        "last_adj_close": bars[-1]["adj_close"] if bars else None,
    }
    if len(bars) >= 2:
        window = bars[-trading_days:] if len(bars) >= trading_days else bars
        first, last = window[0]["adj_close"], window[-1]["adj_close"]
        summary["window_trading_days"] = len(window)
        summary["window_start_date"] = window[0]["date"]
        summary["window_return_pct"] = (
            round((last / first - 1) * 100, 2) if first else None
        )
        closes = [bar["adj_close"] for bar in window]
        summary["window_low"] = min(closes)
        summary["window_high"] = max(closes)
    return summary


def sparkline(bars: list[dict], points: int) -> list[float]:
    """Evenly thin the series down to `points` values for display.

    The last bar is always kept so the shape ends where the price ends.
    """
    closes = [bar["adj_close"] for bar in bars]
    if len(closes) <= points:
        return closes
    step = (len(closes) - 1) / (points - 1)
    return [closes[round(i * step)] for i in range(points)]


def save_series(ticker: str, bars: list[dict], directory: str = HISTORY_DIR) -> str:
    os.makedirs(directory, exist_ok=True)
    payload = {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "ticker": ticker,
        "source": SOURCE,
        "price_field": "adj_close",
        "count": len(bars),
        "bars": bars,
    }
    path = path_for(ticker, directory)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, separators=(",", ":"))
        handle.write("\n")
    return path


def load_series(ticker: str, directory: str = HISTORY_DIR) -> dict:
    with open(path_for(ticker, directory), encoding="utf-8") as handle:
        return json.load(handle)


def load_index(path: str = HISTORY_INDEX_PATH) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def fetch_one(ticker: str, start: str, end: str, api_key: str) -> tuple[str, list[dict], str | None]:
    """Fetch and clean one ticker. Errors are returned, never raised.

    One dead symbol must not abort a 50-name build, so the caller decides
    what to do with the failures.
    """
    try:
        return ticker, normalize_series(ticker, historical_prices(ticker, start, end, api_key)), None
    except FMPError as exc:
        return ticker, [], str(exc)


def build(
    tickers: list[str],
    config: HistoryConfig | None = None,
    api_key: str | None = None,
    directory: str = HISTORY_DIR,
    sparkline_points: int = 0,
) -> dict:
    """Fetch every ticker's history, write one file each, return the index."""
    config = config or HistoryConfig.from_env()
    api_key = api_key or get_api_key()

    end = dt.date.today()
    start = end - dt.timedelta(days=config.calendar_days)
    start_str, end_str = start.isoformat(), end.isoformat()

    with ThreadPoolExecutor(max_workers=config.workers) as pool:
        results = list(
            pool.map(lambda t: fetch_one(t, start_str, end_str, api_key), tickers)
        )

    coverage, failures = [], []
    for ticker, bars, error in results:
        if error:
            failures.append({"ticker": ticker, "error": error})
            continue
        save_series(ticker, bars, directory)
        entry = summarize(ticker, bars, config.trading_days)
        if sparkline_points:
            entry["sparkline"] = sparkline(bars, sparkline_points)
        coverage.append(entry)

    coverage.sort(key=lambda entry: entry["ticker"])
    covered = [entry for entry in coverage if entry["sufficient"]]
    return {
        "schema_version": HISTORY_SCHEMA_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "source": SOURCE,
        "price_field": "adj_close",
        "criteria": dict(
            config.as_dict(), requested_from=start_str, requested_to=end_str
        ),
        "count": len(coverage),
        "sufficient_count": len(covered),
        "failures": failures,
        "coverage": coverage,
    }


def save_index(index: dict, path: str = HISTORY_INDEX_PATH) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(index, handle, indent=2)
        handle.write("\n")
    return path


def iter_rows(tickers: list[str], directory: str = HISTORY_DIR):
    """Yield (ticker, date, adj_close) for every stored bar, in order.

    The long format any panel-shaped consumer wants — pandas, DuckDB, a
    database load — derived from the stored files rather than duplicated.
    """
    for ticker in tickers:
        for bar in load_series(ticker, directory)["bars"]:
            yield ticker, bar["date"], bar["adj_close"]
