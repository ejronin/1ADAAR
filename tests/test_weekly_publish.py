"""Real-data-only weekly publishing contract; no network or Discord test sends."""
import datetime as dt
import json
import tempfile
import unittest
from pathlib import Path
from io import BytesIO
from PIL import Image
from unittest.mock import Mock

from src.weekly_publish import FIRST_RELEASE_SUNDAY, last_finished_sunday, payload, run
from src.weekly_card import render_weekly_card
from src.weekly import summarize_week

P = "a" * 64


def sample(mid=9001):
    return {
        "schemaVersion": 2, "id": mid, "startedAt": "2026-10-22T20:00:00Z",
        "endedAt": "2026-10-22T20:45:00Z", "map": "Bakurani",
        "winner": "Lonestar", "winnerVerified": True, "hasFeed": False,
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

    def test_empty_real_archive_posts_truthful_week_and_dedupes(self):
        self.save([])
        sender=Mock(return_value="123456789")
        result=self.invoke(webhook="https://discord.com/api/webhooks/1/valid",send=sender)
        self.assertEqual(result["status"], "posted")
        self.assertEqual(result["savedMatches"], 0)
        sender.assert_called_once()
        message=sender.call_args.args[1]
        self.assertIn("No completed matches were recorded",message["embeds"][0]["description"])
        self.assertIn("does **not** confirm that no matches were played",message["embeds"][0]["description"])
        self.assertEqual(message["allowed_mentions"], {"parse": []})
        image_bytes=sender.call_args.kwargs["image_bytes"]
        with Image.open(BytesIO(image_bytes)) as image:
            self.assertEqual(image.size, (1080, 750))
        self.assertFalse((self.directory/"wardogs-2"/"2026-10-25.json").exists())
        index=json.loads((self.directory/"index.json").read_text())
        self.assertEqual(index["weeks"], [{
            "weekEnding": "2026-10-25", "completedMatchesSaved": 0, "seasons": []}])
        ledger=json.loads((self.directory/"delivery.json").read_text())
        self.assertEqual(ledger["posted"]["2026-10-25"], "123456789")
        self.assertEqual(self.invoke(webhook="https://discord.com/api/webhooks/1/valid",
                                     send=sender)["status"], "already-posted")
        sender.assert_called_once()

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

    def test_zero_week_without_webhook_archives_but_does_not_claim_delivery(self):
        self.save([])
        sender=Mock()
        no_hook=self.invoke(send=sender)
        self.assertEqual(no_hook["status"],"archive-ready-no-webhook")
        self.assertEqual(json.loads((self.directory/"index.json").read_text())
                         ["weeks"][0]["completedMatchesSaved"],0)
        self.assertEqual(json.loads((self.directory/"delivery.json").read_text())
                         ["posted"],{})
        sender.assert_not_called()
        sender.return_value="55555"
        self.assertEqual(self.invoke(send=sender,webhook="https://discord.com/api/webhooks/1/valid")["status"],"posted")
        sender.assert_called_once()

    def test_explicit_rate_limit_can_retry_but_ambiguous_error_cannot(self):
        import urllib.error
        from unittest.mock import patch
        self.save([])
        http429=urllib.error.HTTPError("https://discord.com",429,"too many requests",
                                        {"Retry-After":"1"},None)
        sender=Mock(side_effect=[http429,"887766"])
        with patch("src.weekly_publish.time.sleep") as sleep:
            self.assertEqual(self.invoke(
                send=sender,webhook="https://discord.com/api/webhooks/1/valid")["status"],"posted")
        sleep.assert_called_once_with(1.0)
        self.assertEqual(sender.call_count,2)
        self.assertEqual(json.loads((self.directory/"delivery.json").read_text())
                         ["posted"]["2026-10-25"],"887766")

    def test_network_failure_is_not_retried_in_process(self):
        import urllib.error
        self.save([])
        sender=Mock(side_effect=urllib.error.URLError("timeout uncertain"))
        with self.assertRaises(urllib.error.URLError):
            self.invoke(send=sender,webhook="https://discord.com/api/webhooks/1/valid")
        sender.assert_called_once()
        ledger=json.loads((self.directory/"delivery.json").read_text())
        self.assertEqual(ledger["posted"],{})

    def test_unconfirmed_message_id_does_not_mark_delivered(self):
        self.save([])
        sender=Mock(return_value=None)
        with self.assertRaises(ValueError):
            self.invoke(send=sender,webhook="https://discord.com/api/webhooks/1/valid")
        self.assertEqual(json.loads((self.directory/"delivery.json").read_text())["posted"],{})

    def test_no_backfilled_prelaunch_week(self):
        self.save([sample()])
        self.now=dt.datetime(2026,10,20,15,10,tzinfo=dt.timezone.utc)
        sender=Mock()
        self.assertEqual(self.invoke(send=sender)["status"],"before-launch-week")
        sender.assert_not_called()

    def test_render_weekly_png_and_season_separation(self):
        report=summarize_week([sample()], "2026-10-25")
        png = render_weekly_card(report)
        self.assertTrue(png.startswith(bytes((137,80,78,71,13,10,26,10))))
        with Image.open(BytesIO(png)) as image:
            self.assertEqual(image.size, (1080, 1290))
        season = next(s for s in report["segments"] if s["completedMatchesInArchive"])
        self.assertEqual(season["topKillers"][0]["name"], "Sample Player")
        self.assertEqual(season["mapLeaders"][0]["leader"]["kills"], 16)
        with Image.open(BytesIO(render_weekly_card(
                summarize_week([], "2026-10-25")))) as empty_image:
            self.assertEqual(empty_image.size, (1080, 750))

    def test_navigation_exists_in_all_pages(self):
        pages=Path(__file__).resolve().parents[1] / "docs"
        for name in ("index.html","players.html"):
            self.assertIn('href="weekly.html"',(pages/name).read_text(),name)
        weekly=(pages/"weekly.html").read_text()
        self.assertIn('id="weekly-summary"',weekly)
        self.assertIn('id="weekly-message"',weekly)
        self.assertIn('assets/1ad-logo.svg',weekly)
        self.assertIn('assets/weekly.css',weekly)
        self.assertIn('js/weekly.js',weekly)


if __name__ == "__main__":
    unittest.main()
