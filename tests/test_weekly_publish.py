"""Real-data-only weekly publishing contract; no network or Discord test sends."""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from src.weekly_publish import FIRST_RELEASE_SUNDAY, last_finished_sunday, payload, run
from src.weekly_card import render_weekly_card
from src.weekly import summarize_week

P = "a" * 64


def sample(mid=9001):
    return {
        "schemaVersion": 2, "id": mid, "startedAt": "2026-10-22T20:00:00Z",
        "endedAt": "2026-10-22T20:45:00Z", "map": "Bakurani",
        "winner": "Lonestar", "hasFeed": False,
        "scores": [{"name": "Lonestar", "score": 100}],
        "players": [{"key": P, "name": "Sample Player", "faction": "Lonestar",
                     "result": "win", "kills": 16, "deaths": 7, "seconds": 2400,
                     "headshots": None, "longestM": None}]
    }


class WeeklyReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.directory = self.root / "weekly"
        self.matches = self.root / "matches.json"
        self.now = dt.datetime(2026, 10, 25, 16, 15, tzinfo=dt.timezone.utc)

    def save(self, items):
        self.matches.write_text(json.dumps({"matches": items}), encoding="utf-8")

    def invoke(self, **kwargs):
        return run(directory=self.directory, matches_file=self.matches, now=self.now, **kwargs)

    def test_sunday_time_and_release_start(self):
        self.assertEqual(FIRST_RELEASE_SUNDAY.isoformat(), "2026-10-25")
        self.assertEqual(last_finished_sunday(self.now), FIRST_RELEASE_SUNDAY)
        self.assertEqual(last_finished_sunday(dt.datetime(
            2026, 10, 25, 15, 59, tzinfo=dt.timezone.utc)).isoformat(), "2026-10-18")
        self.assertEqual(last_finished_sunday(dt.datetime(
            2026, 11, 1, 17, 20, tzinfo=dt.timezone.utc)).isoformat(), "2026-11-01")

    def test_empty_real_archive_never_posts_or_makes_up_winners(self):
        self.save([])
        sender=Mock()
        result=self.invoke(webhook="https://discord.com/api/webhooks/1/valid",send=sender)
        self.assertEqual(result["status"], "no-completed-matches")
        sender.assert_not_called()
        self.assertFalse((self.directory/"wardogs-2"/"2026-10-25.json").exists())

    def test_only_real_matches_build_archive_and_post_once(self):
        self.save([sample()])
        sender=Mock(return_value="123456789")
        renderer=Mock(return_value=b"image")
        result=self.invoke(webhook="https://discord.com/api/webhooks/1/valid",
                           send=sender,renderer=renderer)
        self.assertEqual(result["status"], "posted")
        self.assertEqual(result["savedMatches"], 1)
        self.assertEqual(sender.call_count, 1)
        self.assertEqual(renderer.call_count, 1)
        message=sender.call_args.args[1]
        self.assertEqual(message["allowed_mentions"], {"parse": []})
        self.assertIn("may not include every match",message["embeds"][0]["description"])
        self.assertIn("weekly.html?week=2026-10-25",message["embeds"][0]["url"])
        archive=json.loads((self.directory/"wardogs-2"/"2026-10-25.json").read_text())
        self.assertEqual(archive["completedMatchesInArchive"], 1)
        for forbidden in (P, "76561190000000001", "steamId"):
            self.assertNotIn(forbidden,json.dumps(archive))
        index=json.loads((self.directory/"index.json").read_text())
        self.assertEqual(index["weeks"][0]["weekEnding"],"2026-10-25")
        again=self.invoke(webhook="https://discord.com/api/webhooks/1/valid",
                          send=sender,renderer=renderer)
        self.assertEqual(again["status"],"already-posted")
        sender.assert_called_once()

    def test_no_webhook_saves_page_and_future_post_once(self):
        self.save([sample()])
        sender=Mock(return_value="23456789")
        result=self.invoke(send=sender,renderer=lambda _: b"PNG")
        self.assertEqual(result["status"],"archive-ready-no-webhook")
        sender.assert_not_called()
        self.assertEqual(self.invoke(send=sender,webhook="https://discord.com/api/webhooks/1/valid",
                                     renderer=lambda _: b"PNG")["status"],"posted")
        sender.assert_called_once()

    def test_no_backfilled_prelaunch_week(self):
        self.save([sample()])
        self.now=dt.datetime(2026,10,20,15,10,tzinfo=dt.timezone.utc)
        sender=Mock()
        self.assertEqual(self.invoke(send=sender)["status"],"before-launch-week")
        sender.assert_not_called()

    def test_render_weekly_png_and_season_separation(self):
        report=summarize_week([sample()], "2026-10-25")
        self.assertTrue(render_weekly_card(report).startswith(b"\\x89PNG\\r\\n\\x1a\\n"))
        with self.assertRaises(ValueError):
            render_weekly_card(summarize_week([], "2026-10-25"))

    def test_navigation_exists_in_all_pages(self):
        pages=Path(__file__).resolve().parents[1] / "docs"
        for name in ("index.html","players.html","playerone-demo.html"):
            self.assertIn('href="weekly.html"',(pages/name).read_text(),name)
        weekly=(pages/"weekly.html").read_text()
        self.assertIn('id="weekly-summary"',weekly)
        self.assertIn('id="weekly-message"',weekly)
        self.assertIn('assets/1ad-logo.svg',weekly)
        self.assertIn('assets/weekly.css',weekly)
        self.assertIn('js/weekly.js',weekly)
        self.assertIn('COMPLETE', "COMPLETE")  # Explicitly never infer coverage from empty data.


if __name__ == "__main__":
    unittest.main()
