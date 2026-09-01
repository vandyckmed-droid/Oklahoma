"""Offline tests for calculations over the price history."""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oklahoma import config, history, metrics, ui, universe as universe_mod


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


class CrossSectionTests(unittest.TestCase):
    ROWS = [
        {"ticker": "A", "sector": "Tech", "return_pct": 10.0},
        {"ticker": "B", "sector": "Tech", "return_pct": -5.0},
        {"ticker": "C", "sector": "Tech", "return_pct": 20.0},
        {"ticker": "D", "sector": "Energy", "return_pct": 3.0},
        {"ticker": "E", "sector": "Energy", "return_pct": 7.0},
    ]

    def test_sector_summary_medians_and_breadth(self):
        summary = metrics.sector_summary(self.ROWS)
        self.assertEqual([row["sector"] for row in summary], ["Tech", "Energy"])
        tech = summary[0]
        self.assertEqual(tech["count"], 3)
        self.assertEqual(tech["median_return_pct"], 10.0)
        self.assertAlmostEqual(tech["breadth_pct"], 66.7)
        self.assertEqual(summary[1]["breadth_pct"], 100.0)

    def test_rank_by_return_orders_the_extremes(self):
        ranked = metrics.rank_by_return(self.ROWS, count=2)
        self.assertEqual([row["ticker"] for row in ranked["leaders"]], ["C", "A"])
        self.assertEqual([row["ticker"] for row in ranked["laggards"]], ["B", "D"])

    def test_rank_handles_fewer_rows_than_requested(self):
        ranked = metrics.rank_by_return(self.ROWS[:1], count=5)
        self.assertEqual(len(ranked["leaders"]), 1)
        self.assertEqual(len(ranked["laggards"]), 1)


class DisplayPayloadTests(unittest.TestCase):
    """What the page inlines must agree with the calculation it came from."""

    @classmethod
    def setUpClass(cls):
        cls.index = history.load_index()
        cls.display = ui._display(universe_mod.load(), cls.index)
        cls.target = cls.index["criteria"]["trading_days_target"]

    def test_cross_section_uses_only_full_window_names(self):
        cross = self.display["cross_section"]
        sufficient = sum(1 for row in self.display["coverage"] if row["sufficient"])
        self.assertEqual(cross["names_used"], sufficient)
        self.assertEqual(sum(row["count"] for row in cross["sectors"]), sufficient)

    def test_cross_section_extremes_come_from_the_coverage(self):
        cross = self.display["cross_section"]
        returns = {
            row["ticker"]: row["window_return_pct"]
            for row in self.display["coverage"]
            if row["sufficient"]
        }
        self.assertEqual(cross["leaders"][0]["return_pct"], max(returns.values()))
        self.assertEqual(cross["laggards"][0]["return_pct"], min(returns.values()))

    def test_coverage_name_missing_from_universe_fails_the_build(self):
        # Drift between the index and the universe must fail loudly, not
        # render a phantom sector of unreachable names.
        universe = universe_mod.load()
        broken = dict(
            universe,
            constituents=[
                r for r in universe["constituents"] if r["ticker"] != "AAPL"
            ],
        )
        with self.assertRaises(ValueError) as ctx:
            ui._display(broken, self.index)
        self.assertIn("AAPL", str(ctx.exception))

    def test_three_month_return_matches_the_bars(self):
        for row in self.display["coverage"]:
            bars = history.load_series(row["ticker"])["bars"]
            if len(bars) >= config.TRADING_DAYS_QUARTER:
                quarter = metrics.cumulative_returns(
                    bars, config.TRADING_DAYS_QUARTER
                )
                self.assertEqual(
                    row["return_3m_pct"],
                    round(quarter[-1]["cum_return_pct"], 2),
                )
            else:
                self.assertNotIn("return_3m_pct", row)

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
