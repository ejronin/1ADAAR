import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from src.history import record_snapshots, FIELDS, MAX_SNAPSHOTS

KEY = "a" * 64
OTHER = "b" * 64
def player(key=KEY, **overrides):
    item = {"key": key, "kills": 23, "deaths": 10, "matches": 3, "wins": 2,
            "losses": 1, "draws": 0, "minutes": 120}
    item.update(overrides)
    return item
def date(day):
    return dt.datetime.fromisoformat(day + "T12:00:00+00:00")

class CareerHistoryTests(unittest.TestCase):
    def test_daily_dedup_and_revision_does_not_make_two_points(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            one = {"players": [player()]}
            self.assertEqual(record_snapshots(folder, one, now=date("2026-10-16")), 1)
            self.assertEqual(record_snapshots(folder, one, now=date("2026-10-16")), 0)
            newer = {"players": [player(kills=27, deaths=11)]}
            self.assertEqual(record_snapshots(folder, newer, now=date("2026-10-16")), 1)
            self.assertEqual(record_snapshots(folder, newer, now=date("2026-10-17")), 0)
            self.assertEqual(record_snapshots(folder, {"players": [player(kills=31, deaths=12)]}, now=date("2026-10-17")), 1)
            values = json.loads((folder / "a.json").read_text())["players"][KEY]
            self.assertEqual(len(values), 2)
            self.assertEqual(values[0]["kills"], 27)
            self.assertEqual(values[1]["date"], "2026-10-17")
            self.assertEqual(set(values[0]), {"date", *FIELDS})
            self.assertNotIn("steamId", (folder / "a.json").read_text())
    def test_fresh_empty_players_do_not_write_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            zero = player(kills=0, deaths=0, matches=0)
            self.assertEqual(record_snapshots(folder, {"players": [zero]}, now=date("2026-10-16")), 0)
            self.assertFalse((folder / "a.json").exists())
    def test_shards_retention_and_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            for day in range(1, 63):
                when = date("2026-01-01") + dt.timedelta(days=day)
                record_snapshots(folder, {"players": [player(kills=day + 25), player(OTHER)]}, now=when)
            a = json.loads((folder / "a.json").read_text())["players"][KEY]
            b = json.loads((folder / "b.json").read_text())["players"][OTHER]
            self.assertLessEqual(len(a), MAX_SNAPSHOTS)
            self.assertEqual(len(b), 1)  # Identical career counters are not repeated daily.
            record_snapshots(folder, {"players": [player(kills=300)]}, now=date("2026-10-16"))
            latest = json.loads((folder / "a.json").read_text())["players"][KEY]
            self.assertEqual(len(latest), 1)
            self.assertEqual(latest[0]["kills"], 300)
    def test_corrupt_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / "a.json").write_text('{"schemaVersion": 2, "players": {}}')
            with self.assertRaises(ValueError):
                record_snapshots(folder, {"players": [player()]}, now=date("2026-10-16"))
            self.assertIn('"schemaVersion": 2', (folder / "a.json").read_text())
    def test_reject_invalid_key_or_stats(self):
        with tempfile.TemporaryDirectory() as tmp:
            for row in (player(key="76561190000000001"), player(kills=-3), player(matches=True)):
                with self.assertRaises(ValueError):
                    record_snapshots(Path(tmp), {"players": [row]}, now=date("2026-10-16"))
