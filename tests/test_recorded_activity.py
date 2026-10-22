"""Evidence-based server activity only; NO personal hour-by-hour heatmaps."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest

from src.recorded_activity import build_recorded_activity
from src.season_archive import archive_captured_matches

KEY = "b" * 64


def completed(ident, start="2026-10-20T17:00:00Z", duration=1800):
    began = datetime.fromisoformat(start.replace("Z", "+00:00"))
    ended = began + timedelta(seconds=duration)
    return {
        "schemaVersion": 2, "id": ident, "startedAt": start,
        "endedAt": ended.isoformat().replace("+00:00", "Z"),
        "durationSeconds": duration, "map": "Bakurani",
        "mode": "King of the Hill", "lighting": "Day",
        "winner": "Lonestar", "peakPlayers": 55,
        "scores": [{"name": "Lonestar", "score": 100}],
        "players": [{"key": KEY, "name": "Sample", "faction": "Lonestar",
                     "result": "win", "kills": 9, "deaths": 4,
                     "seconds": 1200, "cashDelta": 0, "headshots": None,
                     "longestM": None, "killStreak": None,
                     "steamId": "76561190000000001", "staffSecret": "DO_NOT_COPY"}],
        "hasFeed": False, "awards": [],
        "warconUrl": (
            "https://console.warcon.app/s/"
            "e30a7ee9-7ea5-4633-882e-98d2e0c03342/matches/" + str(ident)
        )
    }


class RecordedActivityTests(unittest.TestCase):
    def setUp(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        self.archive = Path(d.name) / "seasons"
        self.output = Path(d.name) / "recorded-activity.json"

    def report(self):
        return json.loads(self.output.read_text(encoding="utf-8"))

    def test_initial_state_is_not_fictional_activity(self):
        self.assertEqual(build_recorded_activity(self.archive, self.output)["capturedMatches"], 0)
        data = self.report()
        self.assertEqual(data["coverage"], "captured-only")
        self.assertEqual(data["scope"], "server")
        self.assertEqual(data["measurement"], "Captured completed-match starts")
        self.assertEqual(data["seasons"][0]["count"], 0)
        self.assertEqual(build_recorded_activity(self.archive, self.output)["changedFiles"], 0)

    def test_match_start_not_match_end_or_player_time(self):
        # Tuesday 13:00 Eastern on Oct 20, 2026; match ENDS at 14:00.
        archive_captured_matches(self.archive, [completed(1,duration=3600)])
        result = build_recorded_activity(self.archive,self.output)
        self.assertEqual(result["capturedMatches"], 1)
        data=self.report()
        self.assertEqual(data["seasons"][0]["byWeekdayAndHour"][1][13],1)
        self.assertEqual(data["seasons"][0]["byWeekdayAndHour"][1][14],0)
        self.assertEqual(data["seasons"][2]["count"],1)
        self.assertNotIn("76561190000000001", self.output.read_text())
        self.assertNotIn(KEY, self.output.read_text())
        self.assertNotIn("DO_NOT_COPY", self.output.read_text())

    def test_seasons_are_separate_and_all_scope_adds_them(self):
        archive_captured_matches(self.archive, [
          completed(1,"2026-10-14T17:00:00Z"),
          completed(2,"2026-10-20T17:00:00Z")])
        build_recorded_activity(self.archive,self.output)
        scopes={row["key"]:row for row in self.report()["seasons"]}
        self.assertEqual(scopes["all"]["count"],2)
        self.assertEqual(scopes["wardogs-1"]["count"],1)
        self.assertEqual(scopes["wardogs-2"]["count"],1)
        self.assertEqual(sum(sum(row) for row in scopes["all"]["byWeekdayAndHour"]),2)

    def test_eastern_daylight_saving_repeat_hour_counts_both_verified_starts(self):
        # 2026 Nov 1 Sunday 01:15 EDT and 01:15 EST are distinct real starts.
        archive_captured_matches(self.archive, [
          completed(3,"2026-11-01T05:15:00Z",duration=600),
          completed(4,"2026-11-01T06:15:00Z",duration=600)])
        build_recorded_activity(self.archive,self.output)
        all_scope=self.report()["seasons"][0]
        self.assertEqual(all_scope["byWeekdayAndHour"][6][1],2)
        self.assertEqual(all_scope["count"],2)

    def test_unfinished_and_ambiguous_shards_never_enter_activity(self):
        archive_captured_matches(self.archive,[completed(9)])
        original=self.archive/"wardogs-2"/"2026-10.json"
        malformed=json.loads(original.read_text())
        malformed["matches"][0]["scores"]=[]
        original.write_text(json.dumps(malformed),encoding="utf-8")
        with self.assertRaises(ValueError):
            build_recorded_activity(self.archive,self.output)
        self.assertFalse(self.output.exists())

    def test_web_interface_does_not_make_personal_activity_claims(self):
        docs=Path(__file__).resolve().parents[1]/"docs"
        page=(docs/"activity.html").read_text()
        js=(docs/"js/activity.js").read_text()
        assert "not individual player schedules" in page
        self.assertIn("if(!group.count)",js)
        self.assertIn("status.hidden=true",js)
        self.assertIn("Data will appear as completed matches are recorded.",page)
        self.assertIn("act-insight-title",page)
        self.assertIn("activity-insights.js",page)
        self.assertIn("captured completed match",js)
        self.assertNotIn("steamId",js)
        self.assertNotIn("innerHTML",js)
        self.assertIn("document.createElement",js)
        self.assertIn("America/New_York",js)
        release=(Path(__file__).resolve().parents[1]/
                 "planning/V1.1.0_RELEASE_GATES.md").read_text()
        self.assertIn("approved source",release.lower())


if __name__ == "__main__":
    unittest.main()
