"""Verify that map/team analytics use only captured and recorded results."""
import json
from pathlib import Path
import tempfile
import unittest

from src.map_team import build_map_team
from src.season_archive import archive_captured_matches

KEY = "a" * 64


def completed(ident, map_name="Bakurani", result="win", team="Lonestar",
              deaths=5, ending="2026-10-18T20:00:00Z"):
    beginning = ending.replace("20:00:00", "19:00:00")
    return {"schemaVersion": 2, "id": ident,
            "startedAt": beginning, "endedAt": ending, "durationSeconds": 3600,
            "map": map_name, "mode": "King of the Hill", "lighting": "Day",
            "winner": "Lonestar", "scores": [{"name": "Lonestar", "score": 100}],
            "peakPlayers": 50, "hasFeed": False, "awards": [],
            "players": [{"key": KEY, "name": "Sample", "faction": team, "result": result,
                         "kills": 10, "deaths": deaths, "seconds": 1800, "cashDelta": 0,
                         "headshots": None, "longestM": None, "killStreak": None,
                         "privateExtra": "DO_NOT_COPY"}],
            "warconUrl": "https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches/" + str(ident)}


class MapTeamTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.archive = root / "seasons"
        self.output = root / "map-team"

    def record(self):
        return json.loads((self.output / "a.json").read_text())["players"][KEY]["scopes"]

    def test_empty_history_does_not_create_fake_results(self):
        data = build_map_team(self.archive, self.output)
        self.assertEqual(data["capturedMatches"], 0)
        self.assertEqual(data["players"], 0)
        self.assertEqual(build_map_team(self.archive, self.output)["changedFiles"], 0)

    def test_unknown_outcomes_are_not_counted_as_losses(self):
        archive_captured_matches(self.archive, [
            completed(1), completed(2, result="loss"),
            completed(3, result="", map_name="Ozeti", team="Valkyra")])
        build_map_team(self.archive, self.output)
        scope = self.record()["all"]
        self.assertEqual(scope["total"]["matches"], 3)
        self.assertEqual(scope["total"]["wins"], 1)
        self.assertEqual(scope["total"]["losses"], 1)
        self.assertEqual(scope["total"]["unknownOutcomes"], 1)
        self.assertEqual(scope["total"]["winRate"], 0.5)
        self.assertEqual(scope["uniqueMaps"], 2)
        self.assertIsNone(scope["bestMap"])
        self.assertEqual(len(scope["combinations"]), 2)
        self.assertNotIn("DO_NOT_COPY", (self.output / "a.json").read_text())

    def test_seasons_are_separate(self):
        archive_captured_matches(self.archive, [
            completed(1, result="loss", ending="2026-10-14T20:00:00Z"),
            completed(2, result="win")])
        build_map_team(self.archive, self.output)
        scopes = self.record()
        self.assertEqual(scopes["all"]["total"]["matches"], 2)
        self.assertEqual(scopes["wardogs-1"]["total"]["wins"], 0)
        self.assertEqual(scopes["wardogs-2"]["total"]["wins"], 1)

    def test_ties_and_no_deaths_are_reported_carefully(self):
        archive_captured_matches(self.archive, [
            completed(i, "Bakurani", deaths=0) for i in range(1, 6)] +
            [completed(i, "Ozeti", deaths=0) for i in range(6, 11)])
        build_map_team(self.archive, self.output)
        row = self.record()["all"]
        self.assertTrue(row["bestMap"]["tied"])
        self.assertIsNone(row["bestMap"]["name"])
        self.assertEqual(row["bestMap"]["names"], ["Bakurani", "Ozeti"])
        self.assertIsNone(row["total"]["kd"])

    def test_no_recorded_outcome_means_no_win_rate(self):
        archive_captured_matches(self.archive, [completed(1, result="", deaths=0)])
        build_map_team(self.archive, self.output)
        row = self.record()["all"]["total"]
        self.assertIsNone(row["winRate"])
        self.assertIsNone(row["kd"])

    def test_ambiguous_duplicate_player_lines_are_not_counted_twice(self):
        same = completed(27)
        same["players"].append(dict(same["players"][0], faction="Valkyra"))
        archive_captured_matches(self.archive, [same])
        outcome = build_map_team(self.archive, self.output)
        self.assertEqual(outcome["capturedMatches"], 1)
        self.assertEqual(outcome["players"], 0)
        self.assertEqual(json.loads((self.output / "a.json").read_text())["players"], {})

    def test_safe_links_and_accessible_controls(self):
        root = Path(__file__).resolve().parents[1] / "docs"
        page = (root / "map-team.html").read_text()
        for marker in ("mt-season", "mt-sort", "mt-maps", "mt-factions",
                       "mt-combinations", "mt-win-ring", "mt-team-rings"):
            self.assertIn('id="' + marker + '"', page)
        profile = (root / "players.html").read_text()
        self.assertIn('id="map-team-details"', profile)
        player_script = (root / "js/players.js").read_text()
        self.assertIn("detailed.hidden=!!entry.demo", player_script)
        script = (root / "js/map-team.js").read_text()
        self.assertIn("data/map-team/index.json", script)
        self.assertIn("textContent", script)
        self.assertNotIn("innerHTML", script)
        style = (root / "assets/map-team.css").read_text()
        self.assertIn("mt-donut-svg", style)
        self.assertIn("mt-donut-fill", style)
        self.assertIn("createElementNS", script)
        self.assertIn("stroke-dasharray", script)


if __name__ == "__main__":
    unittest.main()
