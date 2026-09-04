"""Calculations derived from the stored price history.

Everything here reads the adjusted-close series and computes; nothing here
fetches or stores. Derived numbers are recomputed from data/history/ on
demand so there is no second copy to drift.
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from math import exp, log
from statistics import median, stdev

from .config import (
    RS_MIN_NAMES,
    RS_POINTS,
    RS_STEP,
    TRADING_DAYS_HALF,
    TRADING_DAYS_MONTH,
    TRADING_DAYS_TARGET,
)


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


def log_returns(bars: list[dict]) -> list[float]:
    """Daily log returns, one shorter than the bars they come from.

    Computed once per ticker and sliced per window: the relative-strength
    series asks for a standard deviation at thirteen dates over two
    windows each, and re-deriving the returns every time is the whole cost
    of the calculation.
    """
    return [
        log(bars[i]["adj_close"] / bars[i - 1]["adj_close"])
        for i in range(1, len(bars))
    ]


def _window_volatility(rets: list[float], end: int, trading_days: int) -> float | None:
    """Sample deviation of the `trading_days` window of returns ending at `end`.

    `end` indexes the bar the window closes on; returns[i] spans bars i and
    i + 1, so the window's returns are the `trading_days - 1` entries
    ending at end - 1. Zero deviation means a line, not a risk measure, so
    it is refused rather than divided by.
    """
    start = end - trading_days + 1
    if start < 0 or end > len(rets):
        return None
    window = rets[start:end]
    if len(window) < 2:
        return None
    deviation = stdev(window)
    return deviation if deviation > 0 else None


def vol_adjusted_momentum(
    bars: list[dict],
    trading_days: int,
    skip: int = TRADING_DAYS_MONTH,
    rets: list[float] | None = None,
) -> float | None:
    """Skip-month return per unit of the window's daily volatility.

    The same 12-1 or 6-1 return the page already shows, divided by how
    much the name moves day to day over that window. Two names up the same
    amount are not equally strong if one got there in a straight line and
    the other through twice the daily swing, and dividing by volatility is
    the conventional way to say so. Returns None wherever either half is
    unavailable — a short window, or a series that never moved.
    """
    momentum = skip_month_return(bars, trading_days, skip)
    if momentum is None:
        return None
    if rets is None:
        rets = log_returns(bars)
    deviation = _window_volatility(rets, len(bars) - 1, trading_days)
    if deviation is None:
        return None
    return momentum / (deviation * 100)


def percentiles(values: dict[str, float]) -> dict[str, float]:
    """Each value's standing in its own cross-section, 0-100.

    A name's percentile is the share of the cross-section whose value is
    strictly lower — the same definition the page's momentum screen uses,
    so a bar and a slider read the same way. Ties share the lower rank.
    """
    ordered = sorted(values.values())
    total = len(ordered)
    if not total:
        return {}
    return {
        key: round(100 * bisect_left(ordered, value) / total, 1)
        for key, value in values.items()
    }


def relative_strength(
    bars_by_ticker: dict[str, list[dict]],
    calendar: list[str],
    trading_days: int = TRADING_DAYS_TARGET,
    half: int = TRADING_DAYS_HALF,
    skip: int = TRADING_DAYS_MONTH,
    points: int = RS_POINTS,
    step: int = RS_STEP,
    min_names: int = RS_MIN_NAMES,
) -> dict:
    """Each name's cross-sectional standing, sampled back through the year.

    At every snapshot date each name's volatility-adjusted 12-1 and 6-1
    momentum is ranked against every other name carrying both figures that
    day, and the two percentiles are averaged. Ranking each figure before
    blending keeps the wider-spread one from dominating the pair, and a
    percentile puts every name and every date on one fixed 0-100 scale:
    the bar says where the name stood among the S&P 500 that month, so the
    row reads as position now and direction over time.

    The dates come from the shared trading calendar rather than each
    name's own bars, so one column means one date across the whole
    universe. A name without a full window on a date has no bar there.
    """
    snapshots = [
        calendar[i]
        for i in sorted(
            index
            for index in (len(calendar) - 1 - k * step for k in range(points))
            if index >= 0
        )
    ]
    if not snapshots:
        return {"dates": [], "series": {}}

    returns = {t: log_returns(bars) for t, bars in bars_by_ticker.items()}
    dates = {t: [bar["date"] for bar in bars] for t, bars in bars_by_ticker.items()}

    kept: list[str] = []
    series: dict[str, list[float | None]] = {t: [] for t in bars_by_ticker}
    for date in snapshots:
        long_figures: dict[str, float] = {}
        short_figures: dict[str, float] = {}
        for ticker, bars in bars_by_ticker.items():
            # The name's own last session on or before the snapshot date:
            # a name that did not trade that day is measured to its most
            # recent close, never to a future one.
            end = bisect_right(dates[ticker], date) - 1
            if end < trading_days - 1:
                continue
            prefix = bars[: end + 1]
            # Return indices are absolute, so the whole list serves every
            # snapshot: rets[i] is the move into bar i + 1 either way.
            rets = returns[ticker]
            long_value = vol_adjusted_momentum(prefix, trading_days, skip, rets)
            short_value = vol_adjusted_momentum(prefix, half, skip, rets)
            if long_value is None or short_value is None:
                continue
            long_figures[ticker] = long_value
            short_figures[ticker] = short_value
        if len(long_figures) < min_names:
            continue
        long_rank = percentiles(long_figures)
        short_rank = percentiles(short_figures)
        kept.append(date)
        for ticker in bars_by_ticker:
            blended = (
                round((long_rank[ticker] + short_rank[ticker]) / 2, 1)
                if ticker in long_rank
                else None
            )
            series[ticker].append(blended)
    return {"dates": kept, "series": series}


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
