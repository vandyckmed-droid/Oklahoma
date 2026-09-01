"""Offline tests for calculations over the price history."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oklahoma import history, metrics, ui, universe as universe_mod


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


class DisplayPayloadTests(unittest.TestCase):
    """What the page inlines must agree with the calculation it came from."""

    @classmethod
    def setUpClass(cls):
        cls.index = history.load_index()
        cls.display = ui._display(cls.index)
        cls.target = cls.index["criteria"]["trading_days_target"]

    def test_every_covered_name_gets_a_series(self):
        for row in self.display["coverage"]:
            self.assertGreater(len(row.get("cum_return_spark", [])), 1)

    def test_display_matches_the_metric(self):
        for row in self.display["coverage"]:
            series = metrics.cumulative_returns(
                history.load_series(row["ticker"])["bars"], self.target
            )
            with self.subTest(ticker=row["ticker"]):
                self.assertEqual(len(series), row["window_trading_days"])
                self.assertEqual(series[0]["date"], row["window_start_date"])
                self.assertEqual(row["cum_return_spark"][0], 0.0)
                self.assertAlmostEqual(
                    row["cum_return_spark"][-1],
                    series[-1]["cum_return_pct"],
                    places=2,
                )
                self.assertEqual(
                    row["window_return_pct"],
                    round(series[-1]["cum_return_pct"], 2),
                )


if __name__ == "__main__":
    unittest.main()
