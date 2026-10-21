"""Guard against UX redesigns that silently discard existing player analytics.

Source-level contracts only. Rendered browser acceptance remains a separate gate.
"""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1] / "docs"


class ProductFeatureParityTests(unittest.TestCase):
    def test_original_playerone_kpi_inventory_remains_present(self):
        fixture = json.loads((ROOT / "data/demo-player.json").read_text())
        markup = (ROOT / "playerone-demo.html").read_text()
        for label in ("Matches played", "Deaths", "K/D", "Total kills",
                      "Wins", "Win rate", "Playtime", "Seeding time",
                      "Headshots", "Vehicle kills", "Best kill streak"):
            with self.subTest(label=label):
                self.assertIn(label, markup)
        for value in ("matches", "kills", "deaths", "wins", "headshots",
                      "vehicleKills", "killStreak"):
            self.assertIn(str(fixture["player"][value]), markup)
        self.assertEqual(len(fixture["matches"]), 32)

    def test_kd_raw_counts_averages_and_career_chart_modes(self):
        performance = (ROOT / "js/performance.js").read_text()
        engine = (ROOT / "js/performance-core.js").read_text()
        for mode in ("K/D OVER TIME", "KILLS / DEATHS",
                     "5-MATCH AVERAGES", "ALL-TIME K/D"):
            self.assertIn(mode, performance)
        self.assertIn("avgKills", engine)
        self.assertIn("avgDeaths", engine)
        self.assertIn("last.length", engine)
        self.assertIn("'#86f4a4'", performance)  # kills = green
        self.assertIn("'#f5c84b'", performance)  # deaths = yellow
        for period in ("Last 10", "Last 25", "All "):
            self.assertIn(period, performance)
        self.assertIn("perf-details", performance)  # exact-value table
        self.assertIn("prefers-reduced-motion",
                      (ROOT / "assets/performance.css").read_text())

    def test_brand_assets_are_preserved_not_recreated(self):
        markup = (ROOT / "playerone-demo.html").read_text()
        self.assertIn("assets/1ad-logo.svg", markup)
        self.assertIn("assets/wardogs-fullmark.png", markup)
        self.assertIn("assets/factions/lonestar.svg", markup)
        self.assertIn("assets/factions/valkyra.svg", markup)
        self.assertIn("assets/factions/manticore.svg", markup)
        css = (ROOT / "assets/players.css").read_text()
        self.assertIn(".profile-emblem{border-radius:50%", css)


if __name__ == "__main__":
    unittest.main()
