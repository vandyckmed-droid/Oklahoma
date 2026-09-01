"""Offline tests: no network, no API key required."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oklahoma import ui, universe as universe_mod
from oklahoma.config import UniverseConfig


def constituent(symbol, name, sector, cik="0000000001", sub_sector="Test Industry"):
    return {
        "symbol": symbol,
        "name": name,
        "sector": sector,
        "subSector": sub_sector,
        "cik": cik,
        "dateFirstAdded": "2020-01-01",
    }


def quote(cap, price=10.0, volume=1_000_000, exchange="NASDAQ"):
    return {"marketCap": cap, "price": price, "volume": volume, "exchange": exchange}


SAMPLE = [
    (constituent("AAA", "Alpha Inc.", "Technology", cik="0000000010"), quote(900)),
    (constituent("BBB", "Beta Corp.", "Healthcare", cik="0000000020"), quote(800)),
    (constituent("CCC", "Gamma Ltd.", "Energy", cik="0000000030"), quote(700)),
]


def records():
    return [universe_mod._normalize(c, q) for c, q in SAMPLE]


class NormalizeTests(unittest.TestCase):
    def test_carries_the_required_fields(self):
        record = universe_mod._normalize(*SAMPLE[0])
        self.assertEqual(record["ticker"], "AAA")
        self.assertEqual(record["name"], "Alpha Inc.")
        self.assertEqual(record["sector"], "Technology")

    def test_carries_the_durable_identity(self):
        record = universe_mod._normalize(*SAMPLE[0])
        self.assertEqual(record["cik"], "0000000010")
        self.assertEqual(record["date_first_added"], "2020-01-01")

    def test_missing_sector_falls_back(self):
        record = universe_mod._normalize(
            constituent("DDD", "Delta", None), quote(10)
        )
        self.assertEqual(record["sector"], universe_mod.UNKNOWN_SECTOR)

    def test_missing_quote_yields_zero_cap(self):
        record = universe_mod._normalize(constituent("EEE", "Eps", "Energy"), {})
        self.assertEqual(record["market_cap"], 0)


class ShareClassTests(unittest.TestCase):
    def test_collapse_groups_by_cik_not_name(self):
        rows = [
            universe_mod._normalize(
                constituent("GOOGL", "Alphabet Inc. (Class A)", "Communication Services", cik="0001652044"),
                quote(4_100, volume=30_000_000),
            ),
            universe_mod._normalize(
                constituent("GOOG", "Alphabet Inc. (Class C)", "Communication Services", cik="0001652044"),
                quote(4_070, volume=20_000_000),
            ),
        ]
        collapsed = universe_mod.collapse_share_classes(rows)
        self.assertEqual(len(collapsed), 1)
        self.assertEqual(collapsed[0]["ticker"], "GOOGL")
        self.assertEqual(collapsed[0]["share_classes"], ["GOOG", "GOOGL"])

    def test_leaves_distinct_companies_alone(self):
        self.assertEqual(len(universe_mod.collapse_share_classes(records())), 3)


class RankTests(unittest.TestCase):
    def test_orders_by_market_cap(self):
        ranked = universe_mod.rank(records())
        self.assertEqual([r["ticker"] for r in ranked], ["AAA", "BBB", "CCC"])
        self.assertEqual([r["rank"] for r in ranked], [1, 2, 3])

    def test_size_truncates_when_given(self):
        self.assertEqual(len(universe_mod.rank(records(), size=2)), 2)

    def test_no_size_keeps_everything(self):
        self.assertEqual(len(universe_mod.rank(records(), size=None)), 3)


def sample_universe():
    return {
        "schema_version": 2,
        "generated_at": "2026-01-01T00:00:00Z",
        "source": {"provider": "Test", "endpoint": "test", "index": "S&P 500"},
        "criteria": UniverseConfig().as_dict(),
        "count": 3,
        "constituents": universe_mod.rank(records()),
    }


class RoundTripTests(unittest.TestCase):
    def test_save_and_load(self):
        universe = sample_universe()
        with tempfile.TemporaryDirectory() as tmp:
            path = universe_mod.save(universe, os.path.join(tmp, "u.json"))
            self.assertEqual(universe_mod.load(path), universe)

    def test_sector_breakdown(self):
        self.assertEqual(
            universe_mod.sector_breakdown(sample_universe()),
            [("Energy", 1), ("Healthcare", 1), ("Technology", 1)],
        )


class UiTests(unittest.TestCase):
    def test_page_embeds_the_universe(self):
        page = ui.render(sample_universe())
        self.assertNotIn(ui.UNIVERSE_PLACEHOLDER, page)
        self.assertNotIn(ui.HISTORY_PLACEHOLDER, page)
        payload = page.split('type="application/json">')[1].split("</script>")[0]
        self.assertEqual(json.loads(payload.replace("<\\/", "</"))["count"], 3)

    def test_page_is_a_complete_document(self):
        page = ui.render(sample_universe())
        self.assertTrue(page.startswith("<!doctype html>"))
        for tag in ("<head>", "</head>", "<body>", "</body>", "</html>"):
            self.assertIn(tag, page)
        self.assertEqual(page.count("<title>"), 1)


class RealUniverseTests(unittest.TestCase):
    """Guards on the committed data file."""

    @classmethod
    def setUpClass(cls):
        cls.universe = universe_mod.load()

    def test_mirrors_the_whole_index(self):
        self.assertEqual(self.universe["criteria"]["source"], "sp500")
        self.assertEqual(len(self.universe["constituents"]), self.universe["count"])
        # The S&P 500 holds roughly 500 listings; far fewer means a truncated
        # or partial mirror was committed.
        self.assertGreater(self.universe["count"], 450)

    def test_every_name_has_ticker_company_sector_and_cik(self):
        for record in self.universe["constituents"]:
            self.assertTrue(record["ticker"])
            self.assertTrue(record["name"])
            self.assertTrue(record["sector"])
            self.assertTrue(record["cik"])

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
