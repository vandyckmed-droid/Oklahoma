"""Offline tests: no network, no API key required."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oklahoma import ui, universe as universe_mod
from oklahoma.config import UniverseConfig


def row(symbol, name, sector, cap, volume=1_000_000, exchange="NASDAQ"):
    return {
        "symbol": symbol,
        "companyName": name,
        "sector": sector,
        "industry": "Test Industry",
        "marketCap": cap,
        "price": 10.0,
        "avgVolume": volume,
        "exchangeShortName": exchange,
    }


SAMPLE = [
    row("AAA", "Alpha Inc.", "Technology", 900),
    row("BBB", "Beta Corp.", "Healthcare", 800),
    row("CCC", "Gamma Ltd.", "Energy", 700),
]


class NormalizeTests(unittest.TestCase):
    def test_carries_the_required_fields(self):
        record = universe_mod._normalize(SAMPLE[0])
        self.assertEqual(record["ticker"], "AAA")
        self.assertEqual(record["name"], "Alpha Inc.")
        self.assertEqual(record["sector"], "Technology")

    def test_missing_sector_falls_back(self):
        record = universe_mod._normalize(row("DDD", "Delta", None, 10))
        self.assertEqual(record["sector"], universe_mod.UNKNOWN_SECTOR)


class ShareClassTests(unittest.TestCase):
    def test_keeps_the_more_liquid_class(self):
        records = [
            universe_mod._normalize(row("BRK-A", "Berkshire Hathaway Inc.", "Financial Services", 1_000, volume=2_000)),
            universe_mod._normalize(row("BRK-B", "Berkshire Hathaway Inc.", "Financial Services", 990, volume=5_000_000)),
        ]
        collapsed = universe_mod.collapse_share_classes(records)
        self.assertEqual(len(collapsed), 1)
        self.assertEqual(collapsed[0]["ticker"], "BRK-B")
        self.assertEqual(collapsed[0]["share_classes"], ["BRK-A", "BRK-B"])

    def test_leaves_distinct_companies_alone(self):
        records = [universe_mod._normalize(r) for r in SAMPLE]
        self.assertEqual(len(universe_mod.collapse_share_classes(records)), 3)


class RankTests(unittest.TestCase):
    def test_orders_by_market_cap_and_truncates(self):
        ranked = universe_mod.rank([universe_mod._normalize(r) for r in SAMPLE], 2)
        self.assertEqual([r["ticker"] for r in ranked], ["AAA", "BBB"])
        self.assertEqual([r["rank"] for r in ranked], [1, 2])


class RoundTripTests(unittest.TestCase):
    def setUp(self):
        self.universe = {
            "schema_version": 1,
            "generated_at": "2026-01-01T00:00:00Z",
            "source": {"provider": "Test", "endpoint": "test"},
            "criteria": UniverseConfig(size=3).as_dict(),
            "count": 3,
            "constituents": universe_mod.rank(
                [universe_mod._normalize(r) for r in SAMPLE], 3
            ),
        }

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = universe_mod.save(self.universe, os.path.join(tmp, "u.json"))
            self.assertEqual(universe_mod.load(path), self.universe)

    def test_sector_breakdown(self):
        self.assertEqual(
            universe_mod.sector_breakdown(self.universe),
            [("Energy", 1), ("Healthcare", 1), ("Technology", 1)],
        )


class UiTests(unittest.TestCase):
    def setUp(self):
        self.universe = {
            "schema_version": 1,
            "generated_at": "2026-01-01T00:00:00Z",
            "source": {"provider": "Test", "endpoint": "test"},
            "criteria": UniverseConfig(size=3).as_dict(),
            "count": 3,
            "constituents": universe_mod.rank(
                [universe_mod._normalize(r) for r in SAMPLE], 3
            ),
        }

    def test_page_embeds_the_universe(self):
        page = ui.render(self.universe)
        self.assertNotIn(ui.UNIVERSE_PLACEHOLDER, page)
        self.assertNotIn(ui.HISTORY_PLACEHOLDER, page)
        payload = page.split('type="application/json">')[1].split("</script>")[0]
        self.assertEqual(json.loads(payload.replace("<\\/", "</"))["count"], 3)

    def test_page_is_a_complete_document(self):
        page = ui.render(self.universe)
        self.assertTrue(page.startswith("<!doctype html>"))
        for tag in ("<head>", "</head>", "<body>", "</body>", "</html>"):
            self.assertIn(tag, page)
        self.assertEqual(page.count("<title>"), 1)


class RealUniverseTests(unittest.TestCase):
    """Guards on the committed data file."""

    @classmethod
    def setUpClass(cls):
        cls.universe = universe_mod.load()

    def test_has_the_requested_number_of_names(self):
        self.assertEqual(self.universe["count"], self.universe["criteria"]["size"])
        self.assertEqual(len(self.universe["constituents"]), self.universe["count"])

    def test_every_name_has_ticker_company_and_sector(self):
        for record in self.universe["constituents"]:
            self.assertTrue(record["ticker"])
            self.assertTrue(record["name"])
            self.assertTrue(record["sector"])

    def test_tickers_are_unique_and_ranks_are_dense(self):
        tickers = [r["ticker"] for r in self.universe["constituents"]]
        self.assertEqual(len(tickers), len(set(tickers)))
        self.assertEqual(
            [r["rank"] for r in self.universe["constituents"]],
            list(range(1, len(tickers) + 1)),
        )

    def test_sorted_by_descending_market_cap(self):
        caps = [r["market_cap"] for r in self.universe["constituents"]]
        self.assertEqual(caps, sorted(caps, reverse=True))


if __name__ == "__main__":
    unittest.main()
