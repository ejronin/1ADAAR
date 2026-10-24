"""Stage-only weekly intelligence acceptance checks."""
import json
import unittest
from src.weekly import OFFICIAL_SEASONS, sunday_window, summarize_week

A = "a" * 64
B = "b" * 64


def match(mid, when, *, team="Lonestar", feed=True, players=None):
    return {
        "schemaVersion": 2, "id": mid, "startedAt": "2026-10-11T15:00:00Z",
        "endedAt": when, "map": "Bakurani", "winner": team,
        "winnerVerified": True, "scores": [{"name": team, "score": 100}], "hasFeed": feed,
        "players": players if players is not None else [
            {"key": A, "name": "Player A", "faction": team, "result": "win",
             "kills": 15, "deaths": 8, "seconds": 1800, "headshots": 4, "longestM": 270},
            {"key": B, "name": "Player B", "faction": team, "result": "loss",
             "kills": 3, "deaths": 10, "seconds": 1000, "headshots": 0, "longestM": 0}],
    }


class WeeklyStagingTests(unittest.TestCase):
    def test_normal_and_dst_eastern_sundays(self):
        begin, end = sunday_window("2026-10-18")
        self.assertEqual(begin.isoformat(), "2026-10-11T16:00:00+00:00")
        self.assertEqual(end.isoformat(), "2026-10-18T16:00:00+00:00")
        fall = sunday_window("2026-11-01")
        spring = sunday_window("2027-03-14")
        self.assertEqual((fall[1]-fall[0]).total_seconds()/3600, 169)
        self.assertEqual((spring[1]-spring[0]).total_seconds()/3600, 167)
        with self.assertRaises(ValueError):
            sunday_window("2026-10-19")

    def test_season_2_boundary_and_no_mixed_awards(self):
        report = summarize_week([
            match(1, "2026-10-15T15:59:59Z"),
            match(2, "2026-10-15T16:00:00Z")], "2026-10-18")
        self.assertFalse(report["publicationEnabled"])
        self.assertEqual([s["seasonKey"] for s in report["segments"]], ["wardogs-1", "wardogs-2"])
        self.assertEqual([s["completedMatchesInArchive"] for s in report["segments"]], [1, 1])
        self.assertEqual(report["segments"][1]["fromUtc"], "2026-10-15T16:00:00Z")
        self.assertTrue(all(s["coverage"] == "archive-limited" for s in report["segments"]))

    def test_factions_awards_dedup_and_participation(self):
        extra = [{"key": A, "name": "Player A", "faction": "Valkyra",
                  "result": "win", "kills": 2, "deaths": 1, "seconds": 500,
                  "headshots": 1, "longestM": 310}]
        x = match(6, "2026-10-17T20:30:00Z", team="Valkyra", players=extra)
        report = summarize_week([match(5, "2026-10-16T20:30:00Z"), x, x], "2026-10-18")
        s = report["segments"][1]
        self.assertEqual(s["completedMatchesInArchive"], 2)
        self.assertEqual(s["uniqueRecordedPlayers"], 2)
        self.assertEqual(s["factions"], [
            {"name": "Lonestar", "appearances": 2, "recordedPlayerSeconds": 2800, "matchesWon": 1},
            {"name": "Valkyra", "appearances": 1, "recordedPlayerSeconds": 500, "matchesWon": 1}])
        self.assertEqual(s["awards"]["mostMatches"]["name"], "Player A")
        self.assertEqual(s["awards"]["mostHeadshots"]["value"], 5)
        self.assertEqual(s["awards"]["longestShot"]["value"], 310)

    def test_missing_feed_no_fabricated_combat_award(self):
        report = summarize_week([match(8, "2026-10-16T21:00:00Z", feed=False)],
                                "2026-10-18")
        self.assertIsNone(report["segments"][1]["awards"]["longestShot"])
        self.assertIsNone(report["segments"][1]["awards"]["mostHeadshots"])

    def test_no_completed_matches_no_awards(self):
        m = match(8, "2026-10-16T21:00:00Z")
        m["scores"] = []
        report = summarize_week([m], "2026-10-18")
        self.assertEqual(report["segments"][1]["completedMatchesInArchive"], 0)
        self.assertIsNone(report["segments"][1]["awards"]["mostKills"])

    def test_no_private_identifiers(self):
        m = match(9, "2026-10-16T21:00:00Z")
        m["players"][0]["steamId"] = "76561190000000001"
        m["players"][0]["joinCode"] = "secret joining code"
        summary = json.dumps(summarize_week([m], "2026-10-18"))
        for value in ("76561190000000001", "secret joining code", A, B):
            self.assertNotIn(value, summary)

    def test_conflicting_match_id_is_excluded_not_last_write_wins(self):
        normal = match(21, "2026-10-16T20:30:00Z")
        tampered = match(21, "2026-10-16T20:30:00Z")
        tampered["players"][0]["kills"] = 9999
        summary = summarize_week([normal, tampered], "2026-10-18")
        self.assertEqual(summary["conflictingMatchIdsExcluded"], 1)
        season = summary["segments"][1]
        self.assertEqual(season["completedMatchesInArchive"], 0)
        self.assertIsNone(season["awards"]["mostKills"])

    def test_weekly_award_names_are_sanitized_again(self):
        candidate = match(22, "2026-10-16T20:30:00Z")
        candidate["players"][0]["name"] = "@<script>First\\nName</script>"
        candidate["players"][1]["name"] = "76561190000000001"
        summary = summarize_week([candidate], "2026-10-18")
        serialized = json.dumps(summary)
        self.assertNotIn("<script>", serialized)
        self.assertNotIn("@", serialized)
        self.assertNotIn("76561190000000001", serialized)
        self.assertEqual(summary["segments"][1]["uniqueRecordedPlayers"], 1)

    def test_ranked_kill_podium_and_map_leaders_are_from_saved_matches(self):
        first = match(31, "2026-10-16T20:30:00Z")
        second = match(32, "2026-10-17T20:30:00Z")
        second["map"] = "Ozeti"
        second["players"][0]["kills"] = 2
        second["players"][1]["kills"] = 50
        result = summarize_week([first, second], "2026-10-18")["segments"][1]
        self.assertEqual([r["name"] for r in result["topKillers"]], ["Player B", "Player A"])
        self.assertEqual([r["kills"] for r in result["topKillers"]], [53, 17])
        maps = {r["name"]: r for r in result["mapLeaders"]}
        self.assertEqual(maps["Bakurani"]["leader"], {"name": "Player A", "kills": 15})
        self.assertEqual(maps["Ozeti"]["leader"], {"name": "Player B", "kills": 50})
        self.assertEqual(maps["Ozeti"]["matches"], 1)
        for row in result["topKillers"]:
            self.assertNotIn("key", row)

    def test_pending_or_disputed_winner_does_not_receive_win_awards(self):
        pending = match(33, "2026-10-17T20:30:00Z")
        pending["winnerVerified"] = False
        report = summarize_week([pending], "2026-10-18")["segments"][1]
        self.assertEqual(sum(row["matchesWon"] for row in report["factions"]), 0)
        self.assertIsNone(report["awards"]["mostWins"])
        self.assertEqual(report["topKillers"][0]["kills"], 15)
        disputed = match(34, "2026-10-17T20:31:00Z")
        disputed["scores"] = [{"name": "Lonestar", "score": 50},
                              {"name": "Valkyra", "score": 100}]
        report = summarize_week([disputed], "2026-10-18")["segments"][1]
        self.assertIsNone(report["awards"]["mostWins"])

    def test_weekly_kd_requires_twenty_recorded_matches(self):
        items = [match(100 + i, "2026-10-17T20:30:00Z") for i in range(19)]
        self.assertIsNone(summarize_week(items, "2026-10-18")["segments"][1]
                          ["awards"]["bestWeeklyKd20"])
        items.append(match(119, "2026-10-17T20:31:00Z"))
        result = summarize_week(items, "2026-10-18")["segments"][1]
        self.assertEqual(result["awards"]["bestWeeklyKd20"],
                         {"name": "Player A", "value": 1.88, "unit": "K/D"})

    def test_invalid_season_order_rejected(self):
        with self.assertRaises(ValueError):
            summarize_week([], "2026-10-18", seasons=OFFICIAL_SEASONS[::-1])

    def test_character_level_season_kd_and_join_events_not_inferred(self):
        summary = summarize_week([match(10, "2026-10-16T21:00:00Z")], "2026-10-18")
        self.assertIsNone(summary["seasonKdOver20"])
        self.assertIsNone(summary["characterLevelAwards"])
        self.assertIsNone(summary["actualFactionJoinCounts"])
