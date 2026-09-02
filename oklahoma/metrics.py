"""Calculations derived from the stored price history.

Everything here reads the adjusted-close series and computes; nothing here
fetches or stores. Derived numbers are recomputed from data/history/ on
demand so there is no second copy to drift.
"""

from __future__ import annotations

from math import exp, log
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


def skip_month_return(
    bars: list[dict], trading_days: int, skip: int
) -> float | None:
    """Window return measured to `skip` sessions ago, in percent.

    The classic momentum construction (12-1, 6-1): the window's total
    return with the most recent month left out, because the freshest month
    tends to reverse. Measured from the first close of the last
    `trading_days` sessions to the first close of the last `skip`
    sessions — the skipped window's own base — so it composes exactly
    with the page's short window: (1 + 12-1) x (1 + 1M) = 1 + 12M.
    Returns None when the full window is not there — a shorter span would
    be a different number wearing this one's name.
    """
    if skip < 2 or len(bars) < trading_days or trading_days <= skip:
        return None
    base = bars[-trading_days]["adj_close"]
    end = bars[-skip]["adj_close"]
    return round((end / base - 1) * 100, 2)


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


def log_trend(bars: list[dict], trading_days: int = TRADING_DAYS_TARGET) -> dict | None:
    """Least-squares line through ln(adjusted close) over the window.

    Fitting the log makes a constant growth rate a straight line, so the
    slope is the compound daily growth and R² measures how much of the
    year's path one steady trend explains. Returns None when the series
    is shorter than the window — a 54-day fit is not a 12-month trend.

    Closed-form OLS: b = cov(x, y) / var(x), a = mean(y) - b * mean(x),
    with x the trading-day index and y = ln(adj_close).
    """
    if len(bars) < trading_days:
        return None
    window = bars[-trading_days:]
    ys = [log(bar["adj_close"]) for bar in window]
    n = len(ys)
    mean_x = (n - 1) / 2
    mean_y = sum(ys) / n
    var_x = sum((i - mean_x) ** 2 for i in range(n))
    cov_xy = sum((i - mean_x) * (y - mean_y) for i, y in enumerate(ys))
    slope = cov_xy / var_x
    intercept = mean_y - slope * mean_x

    ss_total = sum((y - mean_y) ** 2 for y in ys)
    ss_residual = sum(
        (y - (intercept + slope * i)) ** 2 for i, y in enumerate(ys)
    )
    # A flat series has no variance to explain; float summation leaves
    # ss_total at ~1e-30 rather than 0, so the guard must be a tolerance.
    r2 = 1.0 if ss_total < 1e-18 * n else 1 - ss_residual / ss_total

    annual_pct = (exp(slope * 252) - 1) * 100
    return {
        "slope_daily": slope,
        "intercept": intercept,
        "trend_ann_pct": round(annual_pct, 2),
        "r2": round(r2, 3),
        # Slope damped by fit quality: the classic quality-adjusted
        # momentum score, in the same %/yr units as the trend itself.
        "quality_pct": round(annual_pct * r2, 2),
    }
