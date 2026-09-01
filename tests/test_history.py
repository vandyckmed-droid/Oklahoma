"""Offline tests for the price-history layer. No network, no API key."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oklahoma import history, universe as universe_mod
from oklahoma.config import HistoryConfig, calendar_days_for


def bar(date, adj_close, volume=1000):
    return {"symbol": "TEST", "date": date, "adjClose": adj_close, "volume": volume}


class CalendarWindowTests(unittest.TestCase):
    def test_requests_more_calendar_days_than_trading_days(self):
        # 252 trading days span roughly 365 calendar days; the window must
        # comfortably exceed that or short series come back.
        self.assertGreater(calendar_days_for(252), 365)

    def test_scales_with_the_target(self):
        self.assertGreater(calendar_days_for(504), calendar_days_for(252))

    def test_config_exposes_the_window(self):
        self.assertEqual(
            HistoryConfig(trading_days=252).calendar_days, calendar_days_for(252)
        )


class NormalizeTests(unittest.TestCase):
    def test_keeps_date_and_adjusted_close(self):
        self.assertEqual(
            history.normalize_bar(bar("2026-01-02", 10.5)),
            {"date": "2026-01-02", "adj_close": 10.5, "volume": 1000},
        )

    def test_drops_bars_with_no_adjusted_close(self):
        self.assertIsNone(history.normalize_bar({"date": "2026-01-02"}))
        self.assertIsNone(history.normalize_bar({"adjClose": 10.0}))

    def test_trims_timestamps_to_the_trading_date(self):
        self.assertEqual(
            history.normalize_bar(bar("2026-01-02 00:00:00", 10.0))["date"],
            "2026-01-02",
        )

    def test_series_is_sorted_oldest_first(self):
        series = history.normalize_series(
            "TEST", [bar("2026-01-03", 3), bar("2026-01-01", 1), bar("2026-01-02", 2)]
        )
        self.assertEqual([b["date"] for b in series],
                         ["2026-01-01", "2026-01-02", "2026-01-03"])

    def test_a_repeated_date_keeps_the_later_row(self):
        series = history.normalize_series(
            "TEST", [bar("2026-01-01", 1.0), bar("2026-01-01", 9.0)]
        )
        self.assertEqual(len(series), 1)
        self.assertEqual(series[0]["adj_close"], 9.0)


class SummarizeTests(unittest.TestCase):
    """The index carries coverage facts only; returns live in metrics."""

    def setUp(self):
        self.bars = history.normalize_series(
            "TEST",
            [bar("2026-01-%02d" % (i + 1), 100 + i) for i in range(10)],
        )

    def test_flags_a_series_that_is_long_enough(self):
        summary = history.summarize("TEST", self.bars, trading_days=5)
        self.assertTrue(summary["sufficient"])
        self.assertEqual(summary["trading_days"], 10)
        self.assertEqual(summary["start_date"], "2026-01-01")
        self.assertEqual(summary["end_date"], "2026-01-10")

    def test_flags_a_series_that_is_too_short(self):
        summary = history.summarize("TEST", self.bars, trading_days=252)
        self.assertFalse(summary["sufficient"])

    def test_carries_no_derivable_numbers(self):
        # Anything computable from the bars belongs to metrics/ui, so the
        # index can never disagree with the data it points at.
        summary = history.summarize("TEST", self.bars, trading_days=5)
        self.assertEqual(
            sorted(summary),
            ["end_date", "start_date", "sufficient", "ticker", "trading_days"],
        )

    def test_empty_series_does_not_explode(self):
        summary = history.summarize("TEST", [], trading_days=252)
        self.assertEqual(summary["trading_days"], 0)
        self.assertFalse(summary["sufficient"])
        self.assertIsNone(summary["start_date"])


class ThinTests(unittest.TestCase):
    def test_short_series_passes_through(self):
        self.assertEqual(history.thin([1.0, 2.0], 60), [1.0, 2.0])

    def test_long_series_is_thinned_to_the_point_count(self):
        values = [float(i) for i in range(336)]
        self.assertEqual(len(history.thin(values, 60)), 60)

    def test_endpoints_are_preserved(self):
        values = [float(i) for i in range(336)]
        thinned = history.thin(values, 60)
        self.assertEqual(thinned[0], values[0])
        self.assertEqual(thinned[-1], values[-1])


class PruneTests(unittest.TestCase):
    def test_removes_files_for_departed_tickers_only(self):
        bars_ = history.normalize_series("TEST", [bar("2026-01-01", 1.0)])
        with tempfile.TemporaryDirectory() as tmp:
            history.save_series("KEEP", bars_, tmp)
            history.save_series("GONE", bars_, tmp)
            with open(os.path.join(tmp, "index.json"), "w") as handle:
                handle.write("{}")
            removed = history.prune(["KEEP"], tmp)
            self.assertEqual(removed, ["GONE.json"])
            self.assertTrue(os.path.exists(history.path_for("KEEP", tmp)))
            self.assertTrue(os.path.exists(os.path.join(tmp, "index.json")))


class StorageTests(unittest.TestCase):
    def test_round_trip_and_long_format_rows(self):
        bars = history.normalize_series(
            "TEST", [bar("2026-01-01", 1.0), bar("2026-01-02", 2.0)]
        )
        with tempfile.TemporaryDirectory() as tmp:
            history.save_series("TEST", bars, tmp)
            loaded = history.load_series("TEST", tmp)
            self.assertEqual(loaded["ticker"], "TEST")
            self.assertEqual(loaded["price_field"], "adj_close")
            self.assertEqual(loaded["bars"], bars)
            self.assertEqual(
                list(history.iter_rows(["TEST"], tmp)),
                [("TEST", "2026-01-01", 1.0), ("TEST", "2026-01-02", 2.0)],
            )


class CommittedHistoryTests(unittest.TestCase):
    """Guards on the committed history files."""

    @classmethod
    def setUpClass(cls):
        cls.index = history.load_index()
        cls.universe = universe_mod.load()

    def test_every_universe_name_has_a_history_file(self):
        covered = {entry["ticker"] for entry in self.index["coverage"]}
        for record in self.universe["constituents"]:
            self.assertIn(record["ticker"], covered)
            self.assertTrue(os.path.exists(history.path_for(record["ticker"])))

    def test_nothing_failed_to_load(self):
        self.assertEqual(self.index["failures"], [])

    def test_adjusted_close_is_the_canonical_field(self):
        self.assertEqual(self.index["price_field"], "adj_close")
        self.assertIn("dividend-adjusted", self.index["source"]["endpoint"])

    def test_target_window_is_at_least_252_trading_days(self):
        self.assertGreaterEqual(self.index["criteria"]["trading_days_target"], 252)

    def test_no_orphaned_files(self):
        tickers = {r["ticker"] for r in self.universe["constituents"]}
        for name in os.listdir(os.path.dirname(history.path_for("X"))):
            if name != "index.json":
                self.assertIn(name[:-5], tickers, f"orphan history file: {name}")

    def test_series_are_clean(self):
        target = self.index["criteria"]["trading_days_target"]
        for entry in self.index["coverage"]:
            series = history.load_series(entry["ticker"])
            bars = series["bars"]
            with self.subTest(ticker=entry["ticker"]):
                self.assertEqual(series["ticker"], entry["ticker"])
                self.assertEqual(series["count"], len(bars))
                self.assertEqual(len(bars), entry["trading_days"])
                dates = [b["date"] for b in bars]
                self.assertEqual(dates, sorted(dates), "bars must be chronological")
                self.assertEqual(len(dates), len(set(dates)), "dates must be unique")
                for b in bars:
                    self.assertIsInstance(b["adj_close"], float)
                    self.assertGreater(b["adj_close"], 0)
                    self.assertRegex(b["date"], r"^\d{4}-\d{2}-\d{2}$")
                self.assertEqual(entry["sufficient"], len(bars) >= target)

    def test_almost_every_name_covers_the_full_window(self):
        # A recent listing (an index-added spinoff, say) legitimately cannot;
        # a widespread shortfall means the request window shrank and is a
        # real regression. Allow up to 2%.
        self.assertGreaterEqual(
            self.index["sufficient_count"], int(self.index["count"] * 0.98)
        )


if __name__ == "__main__":
    unittest.main()
