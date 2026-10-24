"""v2 permanent match archive: no lost records, invented data, or SteamIDs."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest

from src.season_archive import archive_captured_matches

KEY = "b" * 64


def finished_match(number: int, ended: str = "2026-10-16T20:30:00Z") -> dict:
    now = dt.datetime.fromisoformat(ended.replace("Z", "+00:00"))
    start = now - dt.timedelta(minutes=38)
    return {
        "schemaVersion": 2, "id": number,
        "startedAt": start.isoformat().replace("+00:00", "Z"),
        "endedAt": ended, "durationSeconds": 38 * 60,
        "map": "Bakurani", "mode": "King of the Hill",
        "lighting": "Day", "winner": "Lonestar",
        "scores": [{"name": "Lonestar", "score": 100},
                   {"name": "Manticore", "score": 45}],
        "peakPlayers": 51,
        "players": [{
            "key": KEY, "name": "TestPlayer",
            "faction": "Lonestar", "result": "win",
            "kills": 12, "deaths": 8, "seconds": 1920,
            "cashDelta": 30, "headshots": None,
            "longestM": None, "killStreak": None,
            "steamId": "76561190000000001", "joinCode": "PRIVATE"
        }],
        "awards": [], "hasFeed": False,
        "warconUrl": f"https://console.warcon.app/s/e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches/{number}",
        "rawSecret": "SHOULD NEVER APPEAR",
    }


class SeasonArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.archive = Path(self.tmp.name)

    def records(self, season, month):
        file = self.archive / season / f"{month}.json"
        return json.loads(file.read_text(encoding="utf-8"))["matches"]

    def test_capture_is_append_only_and_no_raw_identifiers(self):
        first = [finished_match(i) for i in range(1, 121)]
        second = [finished_match(i) for i in range(101, 221)]
        self.assertEqual(archive_captured_matches(self.archive, first)["newMatches"], 120)
        self.assertEqual(archive_captured_matches(self.archive, second)["newMatches"], 100)
        self.assertEqual(archive_captured_matches(self.archive, second)["newMatches"], 0)
        rows = self.records("wardogs-2", "2026-10")
        self.assertEqual(len(rows), 220)
        self.assertEqual(len({m["id"] for m in rows}), 220)
        raw = json.dumps(rows)
        for hidden in ("steamId", "76561190000000001", "joinCode", "PRIVATE", "rawSecret"):
            self.assertNotIn(hidden, raw)
        self.assertIn(KEY, raw)  # Public pseudonym remains consistent for player linking

    def test_official_season_boundary_keeps_separate_files(self):
        rows = [finished_match(1, "2026-10-15T15:59:59Z"),
                finished_match(2, "2026-10-15T16:00:00Z")]
        self.assertEqual(archive_captured_matches(self.archive, rows)["newMatches"], 2)
        self.assertEqual(self.records("wardogs-1", "2026-10")[0]["id"], 1)
        self.assertEqual(self.records("wardogs-2", "2026-10")[0]["id"], 2)

    def test_conflicting_existing_result_does_not_overwrite(self):
        archive_captured_matches(self.archive, [finished_match(8)])
        bad = finished_match(8)
        bad["players"][0]["kills"] = 990
        with self.assertRaises(ValueError):
            archive_captured_matches(self.archive, [bad, finished_match(9)])
        self.assertEqual([m["id"] for m in self.records("wardogs-2", "2026-10")], [8])

    def test_pending_result_can_be_finalized_once_without_changing_combat(self):
        pending = finished_match(90)
        pending["winner"] = ""
        pending["winnerVerified"] = False
        pending["players"][0]["result"] = ""
        archive_captured_matches(self.archive, [pending])
        final = finished_match(90)
        final["winnerVerified"] = True
        final["scores"][0]["score"] = 101
        final["players"][0]["result"] = "win"
        self.assertEqual(archive_captured_matches(self.archive,[final])["newMatches"],0)
        row = self.records("wardogs-2","2026-10")[0]
        self.assertEqual(row["winner"],"Lonestar")
        self.assertTrue(row["winnerVerified"])
        self.assertEqual(row["scores"][0]["score"],101)
        self.assertEqual(row["players"][0]["kills"],12)
        self.assertEqual(archive_captured_matches(self.archive,[final])["changedFiles"],0)
        later = finished_match(90)
        later["winnerVerified"] = True
        later["winner"] = "Manticore"
        with self.assertRaises(ValueError):
            archive_captured_matches(self.archive,[later])
        self.assertEqual(self.records("wardogs-2","2026-10")[0]["winner"],"Lonestar")

    def test_pending_result_cannot_be_amended_with_changed_kills_or_map(self):
        pending = finished_match(91)
        pending["winner"] = ""
        pending["winnerVerified"] = False
        archive_captured_matches(self.archive,[pending])
        altered = finished_match(91)
        altered["winnerVerified"] = True
        altered["players"][0]["kills"] = 999
        with self.assertRaises(ValueError):
            archive_captured_matches(self.archive,[altered])
        altered = finished_match(91)
        altered["winnerVerified"] = True
        altered["map"] = "Ozeti"
        with self.assertRaises(ValueError):
            archive_captured_matches(self.archive,[altered])

    def test_same_id_cannot_move_to_another_month_or_season(self):
        archive_captured_matches(self.archive, [finished_match(60, "2026-10-16T20:30:00Z")])
        with self.assertRaises(ValueError):
            archive_captured_matches(self.archive, [finished_match(60, "2026-11-02T20:30:00Z")])
        self.assertEqual(len(self.records("wardogs-2", "2026-10")), 1)
        self.assertFalse((self.archive/"wardogs-2"/"2026-11.json").exists())

    def test_unknown_or_unfinished_matches_are_rejected(self):
        bad = finished_match(5)
        bad["scores"] = []
        with self.assertRaises(ValueError):
            archive_captured_matches(self.archive, [bad])
        bad = finished_match(6)
        bad["players"][0]["key"] = "76561190000000001"
        with self.assertRaises(ValueError):
            archive_captured_matches(self.archive, [bad])
        self.assertEqual(archive_captured_matches(self.archive, [])["newMatches"], 0)
        self.assertFalse(list(self.archive.glob("*/*.json")))

    def test_old_unsupported_season_is_not_guessed(self):
        result = archive_captured_matches(self.archive,
            [finished_match(3,"2026-08-01T20:30:00Z")])
        self.assertEqual(result["newMatches"], 0)
        self.assertFalse(list(self.archive.glob("*/*.json")))


if __name__ == "__main__":
    unittest.main()
