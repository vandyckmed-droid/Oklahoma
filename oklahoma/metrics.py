"""Calculations derived from the stored price history.

Everything here reads the adjusted-close series and computes; nothing here
fetches or stores. Derived numbers are recomputed from data/history/ on
demand so there is no second copy to drift.
"""

from __future__ import annotations

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
