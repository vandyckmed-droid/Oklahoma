"""Calculations derived from the stored price history.

Everything here reads the adjusted-close series and computes; nothing here
fetches or stores. Derived numbers are recomputed from data/history/ on
demand so there is no second copy to drift.
"""

from __future__ import annotations

from statistics import median

from .config import TRADING_DAYS_TARGET


def cumulative_returns(bars: list[dict], trading_days: int = TRADING_DAYS_TARGET) -> list[dict]:
    """Daily cumulative return over the last `trading_days` sessions.

    Each point is the total return from the window's first close to that
    day, in percent: day one is 0.0 by construction. A series shorter than
    the window is measured over what it has — the caller can see the actual
    span from the dates.
    """
    window = bars[-trading_days:] if len(bars) > trading_days else list(bars)
    if not window:
        return []
    base = window[0]["adj_close"]
    return [
        {
            "date": bar["date"],
            "cum_return_pct": round((bar["adj_close"] / base - 1) * 100, 4),
        }
        for bar in window
    ]


def sector_summary(rows: list[dict]) -> list[dict]:
    """Per-sector view of window returns, strongest sector first.

    Each input row carries `sector` and `return_pct`. Breadth — the share
    of names positive — guards the median: a sector can post a healthy
    median on three winners and seventeen losers, and breadth says so.
    """
    by_sector: dict[str, list[float]] = {}
    for row in rows:
        by_sector.setdefault(row["sector"], []).append(row["return_pct"])

    summary = [
        {
            "sector": sector,
            "count": len(returns),
            "median_return_pct": round(median(returns), 2),
            "breadth_pct": round(
                100 * sum(1 for value in returns if value > 0) / len(returns), 1
            ),
        }
        for sector, returns in by_sector.items()
    ]
    summary.sort(key=lambda entry: (-entry["median_return_pct"], entry["sector"]))
    return summary


def rank_by_return(rows: list[dict], count: int = 5) -> dict:
    """The window's extremes: best and worst `count` names by return.

    With fewer than `2 * count` rows the two lists overlap — a single row
    is simultaneously the leader and the laggard. Callers passing a small
    slice (one sector's names, say) should expect that.
    """

    def trim(row: dict) -> dict:
        return {key: row[key] for key in ("ticker", "sector", "return_pct")}

    ordered = sorted(rows, key=lambda row: row["return_pct"], reverse=True)
    return {
        "leaders": [trim(row) for row in ordered[:count]],
        "laggards": [trim(row) for row in ordered[::-1][:count]],
    }
