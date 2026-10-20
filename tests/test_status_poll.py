"""v1.0.1 status-only workflow: reliability, minimization, and no combat API calls."""
import datetime as dt
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
from src.status_poll import poll, fetch_status, URL

NOW = dt.datetime(2026, 10, 17, 13, 30, tzinfo=dt.timezone.utc)


class FastPublicStatusTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = pathlib.Path(self.temp.name)
        (self.path / "server-status-state.json").write_text(
            '{"schemaVersion":1,"state":"online"}', encoding="utf-8")

    def test_status_only_has_no_personal_or_private_fields(self):
        source = {
            "ok": True,
            "server": {"ok": True, "players": 25, "maxPlayers": 100,
                       "map": "Europe", "observedAt": "2026-10-17T13:29:00Z",
                       "roster": [{"steamId": "76561190000000001"}],
                       "joinCode": "secret joining code",
                       "rconAddress": "private-host:12345"}
        }
        result = poll(self.path, now=NOW, fetch=lambda: source)
        self.assertEqual(result["state"], "online")
        self.assertFalse(result["changed"])
        status = json.loads((self.path / "server-status.json").read_text())
        self.assertEqual(status["players"], 25)
        self.assertEqual(status["map"], "Ozeti")
        for key in ("joinCode", "steamId", "roster", "rconAddress"):
            self.assertNotIn(key, json.dumps(status))
        self.assertFalse((self.path / "players.json").exists())
        self.assertFalse((self.path / "matches.json").exists())

    def test_online_loss_then_offline_deduplicated(self):
        unavailable = {"ok": True, "server": {"ok": False,
           "observedAt": "2026-10-17T13:29:00Z",
           "players": 0, "map": "Europe"}}
        first = poll(self.path, now=NOW, fetch=lambda: unavailable)
        self.assertEqual(first["state"], "reconnecting")
        self.assertTrue(first["changed"])
        second = poll(self.path, now=NOW, fetch=lambda: unavailable)
        self.assertEqual(second["state"], "offline")
        self.assertTrue(second["changed"])
        third = poll(self.path, now=NOW, fetch=lambda: unavailable)
        self.assertFalse(third["changed"])

    def test_bad_status_stays_neutral(self):
        result = poll(self.path, now=NOW, fetch=lambda: {"ok": True, "server": {
            "ok": True, "observedAt": "2026-10-17T12:40:00Z"}})
        self.assertEqual(result["state"], "unknown")

    def test_status_failure_is_not_fake_offline(self):
        def failed():
            raise urllib.error.URLError("temporarily unreachable")
        import urllib.error
        result = poll(self.path, now=NOW, fetch=failed)
        self.assertEqual(result["state"], "unknown")
        self.assertIsNone(json.loads((self.path / "server-status.json").read_text())["players"])

    def test_server_endpoint_is_public_and_roster_not_requested(self):
        self.assertEqual(URL.count("/api/public/servers/"), 1)
        self.assertNotIn("leaderboard", URL)
        self.assertNotIn("matches", URL)

    def test_schedule_adds_lightweight_midpoints(self):
        yaml = (pathlib.Path(__file__).resolve().parents[1]
                / ".github/workflows/collect.yml").read_text()
        self.assertIn("'4,14,24,34,44,54 * * * *'", yaml)
        self.assertIn("'9,19,29,39,49,59 * * * *'", yaml)
        self.assertIn("python -m src.status_poll", yaml)
        self.assertIn("steps.workload.outputs.full == 'false'", yaml)
