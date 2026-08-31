"""Offline tests for calculations over the price history."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oklahoma import history, metrics, universe as universe_mod


def bars(*closes):
    return [
        {"date": "2026-01-%02d" % (i + 1), "adj_close": float(c)}
        for i, c in enumerate(closes)
    ]


class CumulativeReturnTests(unittest.TestCase):
    def test_starts_at_zero(self):
        series = metrics.cumulative_returns(bars(100, 110), trading_days=252)
        self.assertEqual(series[0]["cum_return_pct"], 0.0)

    def test_compounds_from_the_window_start(self):
        series = metrics.cumulative_returns(bars(100, 110, 121), trading_days=252)
        self.assertEqual(
            [p["cum_return_pct"] for p in series], [0.0, 10.0, 21.0]
        )

    def test_only_the_last_window_counts(self):
        # A huge move before the window must not leak into the numbers.
        series = metrics.cumulative_returns(bars(1, 100, 110), trading_days=2)
        self.assertEqual([p["date"] for p in series], ["2026-01-02", "2026-01-03"])
        self.assertEqual([p["cum_return_pct"] for p in series], [0.0, 10.0])

    def test_short_series_is_measured_over_what_it_has(self):
        series = metrics.cumulative_returns(bars(100, 90), trading_days=252)
        self.assertEqual(len(series), 2)
        self.assertEqual(series[-1]["cum_return_pct"], -10.0)

    def test_negative_returns_are_negative(self):
        series = metrics.cumulative_returns(bars(200, 150), trading_days=252)
        self.assertEqual(series[-1]["cum_return_pct"], -25.0)

    def test_empty_series_yields_empty(self):
        self.assertEqual(metrics.cumulative_returns([], trading_days=252), [])


class CommittedDataTests(unittest.TestCase):
    """The calculation must agree with the committed index."""

    def test_final_cumulative_return_matches_the_index(self):
        index = history.load_index()
        target = index["criteria"]["trading_days_target"]
        for entry in index["coverage"]:
            series = metrics.cumulative_returns(
                history.load_series(entry["ticker"])["bars"], target
            )
            with self.subTest(ticker=entry["ticker"]):
                self.assertEqual(len(series), entry["window_trading_days"])
                self.assertEqual(series[0]["date"], entry["window_start_date"])
                self.assertAlmostEqual(
                    series[-1]["cum_return_pct"],
                    entry["window_return_pct"],
                    places=2,
                )


if __name__ == "__main__":
    unittest.main()
