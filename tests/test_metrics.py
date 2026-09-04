"""Offline tests for calculations over the price history."""

import os
import statistics
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


class SkipMonthReturnTests(unittest.TestCase):
    def test_ends_at_the_skipped_windows_base(self):
        # 100 -> 121 at the skip window's base, then a giveback it ignores.
        series = bars(100, 110, 121, 110)
        self.assertEqual(metrics.skip_month_return(series, 4, 2), 21.0)

    def test_reads_from_its_own_window_base(self):
        series = bars(50, 100, 110, 121, 110)
        self.assertEqual(metrics.skip_month_return(series, 4, 2), 21.0)

    def test_composes_with_the_short_window(self):
        # (1 + skip-month) x (1 + short window) = 1 + full window.
        series = bars(100, 105, 121, 133.1)
        mom = metrics.skip_month_return(series, 4, 2)
        short = metrics.cumulative_returns(series, 2)[-1]["cum_return_pct"]
        full = metrics.cumulative_returns(series, 4)[-1]["cum_return_pct"]
        self.assertAlmostEqual(
            (1 + mom / 100) * (1 + short / 100), 1 + full / 100, places=6
        )

    def test_short_series_is_none_not_a_smaller_number(self):
        self.assertIsNone(metrics.skip_month_return(bars(100, 110), 4, 2))

    def test_window_must_outreach_the_skip(self):
        self.assertIsNone(metrics.skip_month_return(bars(100, 110, 121), 2, 2))


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


class LogTrendTests(unittest.TestCase):
    @staticmethod
    def exponential(daily, n=252, start=100.0):
        import math
        return [
            {"date": str(i), "adj_close": start * math.exp(daily * i)}
            for i in range(n)
        ]

    def test_exact_exponential_recovers_its_rate(self):
        import math
        trend = metrics.log_trend(self.exponential(0.001), 252)
        self.assertAlmostEqual(trend["slope_daily"], 0.001, places=12)
        self.assertEqual(trend["r2"], 1.0)
        self.assertEqual(
            trend["trend_ann_pct"], round((math.exp(0.252) - 1) * 100, 2)
        )

    def test_flat_series_is_zero_trend_full_fit(self):
        flat = [{"date": str(i), "adj_close": 50.0} for i in range(252)]
        trend = metrics.log_trend(flat, 252)
        self.assertEqual(trend["trend_ann_pct"], 0.0)
        self.assertEqual(trend["r2"], 1.0)

    def test_declining_series_has_negative_trend(self):
        trend = metrics.log_trend(self.exponential(-0.002), 252)
        self.assertLess(trend["trend_ann_pct"], 0)
        self.assertEqual(trend["r2"], 1.0)

    def test_quality_is_trend_damped_by_r2(self):
        trend = metrics.log_trend(self.exponential(0.001), 252)
        self.assertEqual(
            trend["quality_pct"], round(trend["trend_ann_pct"] * trend["r2"], 2)
        )

    def test_short_series_yields_none(self):
        self.assertIsNone(metrics.log_trend(self.exponential(0.001, n=100), 252))

    def test_only_the_window_participates(self):
        # A wild year before the window must not bend the fit.
        import math
        noise = [{"date": "a%d" % i, "adj_close": 5000.0 if i % 2 else 1.0}
                 for i in range(50)]
        clean = self.exponential(0.001)
        trend = metrics.log_trend(noise + clean, 252)
        self.assertAlmostEqual(trend["slope_daily"], 0.001, places=12)
        self.assertEqual(trend["r2"], 1.0)


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

    def test_six_month_return_matches_the_bars(self):
        for row in self.display["coverage"]:
            bars = history.load_series(row["ticker"])["bars"]
            if len(bars) >= config.TRADING_DAYS_HALF:
                half = metrics.cumulative_returns(bars, config.TRADING_DAYS_HALF)
                self.assertEqual(
                    row["return_6m_pct"],
                    round(half[-1]["cum_return_pct"], 2),
                )
            else:
                self.assertNotIn("return_6m_pct", row)

    def test_one_month_return_matches_the_bars(self):
        for row in self.display["coverage"]:
            bars = history.load_series(row["ticker"])["bars"]
            if len(bars) >= config.TRADING_DAYS_MONTH:
                month = metrics.cumulative_returns(bars, config.TRADING_DAYS_MONTH)
                self.assertEqual(
                    row["return_1m_pct"],
                    round(month[-1]["cum_return_pct"], 2),
                )
            else:
                self.assertNotIn("return_1m_pct", row)

    def test_trend_fields_match_the_bars(self):
        for row in self.display["coverage"]:
            bars = history.load_series(row["ticker"])["bars"]
            trend = metrics.log_trend(bars, self.target)
            if trend is None:
                self.assertNotIn("trend_ann_pct", row)
                self.assertNotIn("fit_spark", row)
                continue
            self.assertEqual(row["trend_ann_pct"], trend["trend_ann_pct"])
            self.assertEqual(row["trend_r2"], trend["r2"])
            self.assertEqual(row["quality_pct"], trend["quality_pct"])
            self.assertEqual(
                len(row["fit_spark"]), len(row["cum_return_spark"])
            )

    def test_fit_spark_is_the_fitted_curve_in_chart_space(self):
        import math
        row = next(
            r for r in self.display["coverage"] if r["ticker"] == "AAPL"
        )
        bars = history.load_series("AAPL")["bars"]
        trend = metrics.log_trend(bars, self.target)
        window = bars[-self.target:]
        base = window[0]["adj_close"]
        indices = history.thin_indices(self.target, len(row["fit_spark"]))
        for got, i in zip(row["fit_spark"], indices):
            expected = (
                math.exp(trend["intercept"] + trend["slope_daily"] * i)
                / base - 1
            ) * 100
            self.assertEqual(got, round(expected, 2))

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


class VolatilityAdjustedMomentumTests(unittest.TestCase):
    def test_steadier_of_two_equal_climbs_scores_higher(self):
        # Identical at both ends the return is measured from (index 0 and
        # index 25 of a 30-bar window skipping 5), so only the path
        # between them differs — and the choppier path must divide by the
        # larger deviation.
        smooth_closes = [100 * 1.01 ** i for i in range(30)]
        rough_closes = [
            close if i in (0, 25) else close * (1.05 if i % 2 else 0.95)
            for i, close in enumerate(smooth_closes)
        ]
        steady, choppy = bars(*smooth_closes), bars(*rough_closes)
        self.assertEqual(
            metrics.skip_month_return(steady, 30, 5),
            metrics.skip_month_return(choppy, 30, 5),
        )
        self.assertGreater(
            metrics.vol_adjusted_momentum(steady, 30, skip=5),
            metrics.vol_adjusted_momentum(choppy, 30, skip=5),
        )

    def test_is_the_return_divided_by_the_windows_deviation(self):
        series = bars(*[100 * 1.004 ** i * (1.01 if i % 3 else 0.99) for i in range(40)])
        rets = metrics.log_returns(series)
        deviation = statistics.stdev(rets[len(series) - 30:len(series) - 1])
        self.assertAlmostEqual(
            metrics.vol_adjusted_momentum(series, 30, skip=5),
            metrics.skip_month_return(series, 30, 5) / (deviation * 100),
            places=9,
        )

    def test_flat_series_has_no_volatility_to_divide_by(self):
        self.assertIsNone(metrics.vol_adjusted_momentum(bars(*([100] * 30)), 30, skip=5))

    def test_short_series_yields_none(self):
        self.assertIsNone(metrics.vol_adjusted_momentum(bars(100, 110), 30, skip=5))


class PercentileTests(unittest.TestCase):
    def test_lowest_is_zero_and_highest_is_all_but_its_own_share(self):
        ranks = metrics.percentiles({"a": 1.0, "b": 2.0, "c": 3.0, "d": 4.0})
        self.assertEqual(ranks["a"], 0.0)
        self.assertEqual(ranks["d"], 75.0)

    def test_ties_share_the_lower_rank(self):
        ranks = metrics.percentiles({"a": 5.0, "b": 5.0, "c": 9.0})
        self.assertEqual(ranks["a"], ranks["b"])
        self.assertEqual(ranks["a"], 0.0)

    def test_empty_cross_section(self):
        self.assertEqual(metrics.percentiles({}), {})


class MomentumBlendTests(unittest.TestCase):
    """The score is a cross-section, so it is tested across names."""

    @staticmethod
    def universe_of(rates, length=80):
        return {
            name: bars(*[100 * rate ** i * (1.01 if i % 2 else 0.99) for i in range(length)])
            for name, rate in rates.items()
        }

    def blend(self, rates, **overrides):
        options = dict(trading_days=40, half=20, skip=5, min_names=2)
        options.update(overrides)
        return metrics.momentum_blend(self.universe_of(rates), **options)

    def test_the_strongest_name_ranks_top_and_the_weakest_bottom(self):
        out = self.blend({"up": 1.006, "mid": 1.002, "down": 0.996})
        self.assertGreater(out["up"], out["mid"])
        self.assertGreater(out["mid"], out["down"])

    def test_every_score_sits_on_the_fixed_scale(self):
        out = self.blend({"a": 1.006, "b": 1.002, "c": 0.996, "d": 1.004})
        for value in out.values():
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 100.0)

    def test_an_outlier_ranks_first_without_stretching_the_scale(self):
        # The point of ranking before blending: a name up thirty-fold
        # tops the list and stops there, leaving the scale where it was.
        rates = {"a": 1.006, "b": 1.002, "c": 0.996, "d": 1.004}
        ordinary = self.blend(rates)
        book = self.universe_of(rates)
        book["moon"] = bars(*[100 * 1.05 ** i for i in range(80)])
        wild = metrics.momentum_blend(book, trading_days=40, half=20, skip=5, min_names=2)
        self.assertEqual(wild["moon"], max(wild.values()))
        self.assertLessEqual(max(wild.values()), 100.0)
        # The others keep their order; only the new name joins the ranking.
        self.assertEqual(
            sorted(ordinary, key=ordinary.get),
            sorted(ordinary, key=lambda t: wild[t]),
        )

    def test_a_name_without_a_full_window_has_no_score(self):
        book = self.universe_of({"a": 1.006, "b": 1.002, "c": 0.996})
        book["young"] = bars(*[100 * 1.01 ** i for i in range(10)])
        out = metrics.momentum_blend(book, trading_days=40, half=20, skip=5, min_names=2)
        self.assertNotIn("young", out)
        self.assertIn("a", out)

    def test_a_thin_cross_section_scores_nothing(self):
        self.assertEqual(self.blend({"a": 1.006, "b": 1.002}, min_names=3), {})


class MomentumBlendPayloadTests(unittest.TestCase):
    """The page's score must match the calculation it came from."""

    @classmethod
    def setUpClass(cls):
        cls.display = ui._display(universe_mod.load(), history.load_index())
        cls.scored = [r for r in cls.display["coverage"] if "blend_pct" in r]

    def test_every_full_window_name_is_scored(self):
        full = [r for r in self.display["coverage"] if r["sufficient"]]
        self.assertEqual(len(self.scored), len(full))

    def test_every_score_is_a_percentile_on_the_fixed_scale(self):
        for row in self.scored:
            with self.subTest(ticker=row["ticker"]):
                self.assertGreaterEqual(row["blend_pct"], 0.0)
                self.assertLessEqual(row["blend_pct"], 100.0)

    def test_names_are_spread_across_the_scale(self):
        # A score that clusters would mean the ranking collapsed.
        values = [row["blend_pct"] for row in self.scored]
        self.assertGreater(len(values), 100)
        self.assertLess(min(values), 10)
        self.assertGreater(max(values), 90)

    def test_the_payload_matches_a_direct_recomputation(self):
        bars_by_ticker = {
            row["ticker"]: history.load_series(row["ticker"])["bars"]
            for row in self.display["coverage"]
        }
        expected = metrics.momentum_blend(bars_by_ticker)
        self.assertEqual(
            {row["ticker"]: row["blend_pct"] for row in self.scored}, expected
        )


if __name__ == "__main__":
    unittest.main()
