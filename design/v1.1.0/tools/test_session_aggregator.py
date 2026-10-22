"""No-live-access session heatmap regression tests with synthetic timestamps."""
import importlib.util
from pathlib import Path
import unittest

FILE = Path(__file__).resolve().parents[1] / "components" / "session_aggregator.py"
spec = importlib.util.spec_from_file_location("activity_component", FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
aggregate = module.aggregate_player_sessions

class SessionTest(unittest.TestCase):
    def test_explicit_publication_gate(self):
        with self.assertRaises(PermissionError):
            aggregate([], window_start="2026-10-19T00:00:00Z", window_end="2026-10-21T00:00:00Z")

    def test_local_midnight_crossing_correct_day_hour(self):
        # 2026-10-19 23:40 to 2026-10-20 00:20 Eastern.
        o = aggregate([{"joinedAt":"2026-10-20T03:40:00Z","leftAt":"2026-10-20T04:20:00Z",
                        "steamId":"NEVER-PUBLISH"}],
            window_start="2026-10-19T00:00:00Z",window_end="2026-10-21T00:00:00Z",
            publication_approved=True)
        self.assertEqual(o["minutesByDay"], {"2026-10-19":20, "2026-10-20":20})
        self.assertEqual(o["minutesByWeekdayHour"][0][23],20)
        self.assertEqual(o["minutesByWeekdayHour"][1][0],20)
        self.assertNotIn("steamId",str(o))
        self.assertNotIn("NEVER-PUBLISH",str(o))
        self.assertEqual(o["coverage"],"partial/unknown")

    def test_dst_fallback_counts_repeated_hour_without_disappearing(self):
        # 01:30 EDT through 01:30 EST: 60 real elapsed minutes, same local hour.
        o=aggregate([{"joinedAt":"2026-11-01T05:30:00Z","leftAt":"2026-11-01T06:30:00Z"}],
            window_start="2026-11-01T00:00:00Z",window_end="2026-11-02T00:00:00Z",
            publication_approved=True,capture_complete=True)
        self.assertEqual(o["minutesByWeekdayHour"][6][1],60)
        self.assertEqual(o["minutesByDay"]["2026-11-01"],60)
        self.assertEqual(o["coverage"],"complete")

    def test_merge_overlapping_and_skip_unended_session(self):
        o=aggregate([
           {"joinedAt":"2026-10-20T10:00:00Z","leftAt":"2026-10-20T10:45:00Z"},
           {"joinedAt":"2026-10-20T10:25:00Z","leftAt":"2026-10-20T11:00:00Z"},
           {"joinedAt":"2026-10-20T11:30:00Z","leftAt":None}],
            window_start="2026-10-20T00:00:00Z",window_end="2026-10-21T00:00:00Z",
            publication_approved=True)
        self.assertEqual(o["observedMinutes"],60)
        self.assertEqual(o["sourceSessions"],2)
        self.assertEqual(o["mergedIntervals"],1)
        self.assertEqual(o["skippedIncompleteSessions"],1)

if __name__=="__main__":
    unittest.main()
