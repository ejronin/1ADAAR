"""A completed WARCON match MUST have a verified winner before Discord dispatch.

WARCON may update a closed match when the game's authoritative result arrives.
Never award the score leader ourselves or post a blank/contradictory winner.
"""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from src import recap

SOURCE = {
    "id": 9811,
    "startedAt": "2026-10-24T00:00:00Z",
    "endedAt": "2026-10-24T00:35:00Z",
    "map": "Kavkazi",
    "experiences": "Bakurani_KOTH_01",
    "peakPlayers": 64,
    "finalScores": [
        {"name": "Lonestar", "score": 100},
        {"name": "Valkyra", "score": 82},
        {"name": "Manticore", "score": 64},
    ],
    "winner": None,
}


class WinnerVerificationTests(unittest.TestCase):
    def test_raw_score_leader_is_not_proof(self):
        self.assertTrue(recap.usable_match(SOURCE))
        self.assertEqual(recap.verified_winner(SOURCE), "")
        pending = recap.public_match(SOURCE)
        self.assertTrue(pending["verifiedCompleted"])
        self.assertFalse(pending["winnerVerified"])
        self.assertEqual(pending["winner"], "")
        with self.assertRaisesRegex(ValueError, "verified final winner"):
            recap.discord_payload(pending)

    def test_winner_must_match_one_undisputed_top_score(self):
        self.assertEqual(recap.verified_winner({**SOURCE, "winner": "Valkyra"}), "")
        self.assertEqual(recap.verified_winner({**SOURCE, "winner": "OtherTeam"}), "")
        self.assertEqual(recap.verified_winner({**SOURCE, "winner": "Lonestar",
            "finalScores": [{"name": "Lonestar", "score": 100},
                            {"name": "Valkyra", "score": 100}]}), "")
        self.assertEqual(recap.verified_winner({**SOURCE, "winner": "lonestar"}), "Lonestar")
        self.assertEqual(recap.verified_winner({**SOURCE, "winner": "Lonestar",
            "endedAt": None}), "")

    def test_collector_deferred_then_refetched_then_sent_exactly_once(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            (dest / "delivery.json").write_text(json.dumps(
                {"initialized": True, "posted": {}}), encoding="utf-8")
            state = {"winner": None, "details": 0}

            def response(url, **kwargs):
                if "?page=" in url:
                    # Deliberately stale LIST result even after match detail is repaired.
                    return {"ok": True, "matches": [SOURCE], "pages": 1}
                if url.endswith("/9811"):
                    state["details"] += 1
                    match = {**SOURCE, "winner": state["winner"]}
                    return {"ok": True, "match": match,
                            "lines": [], "awards": [], "hasFeed": False}
                if url == recap.PUBLIC_STATUS:
                    return {"ok": True, "server": {}}
                return {"ok": True, "players": [], "page": 1, "pages": 1}

            webhook = "https://discord.com/api/webhooks/12345/validtoken"
            with patch.object(recap, "DATA", dest), \
                 patch.object(recap, "fetch_json", side_effect=response), \
                 patch.object(recap, "render_match_card", return_value=b"mock png"), \
                 patch.object(recap, "send_discord", return_value="314159") as sender:
                recap.run(webhook=webhook)
                sender.assert_not_called()
                first = json.loads((dest / "matches.json").read_text())["matches"][0]
                self.assertFalse(first["winnerVerified"])
                ledger = json.loads((dest / "delivery.json").read_text())
                self.assertNotIn("9811", ledger["posted"])

                # Game's final result arrives after the first collector observation.
                state["winner"] = "Lonestar"
                recap.run(webhook=webhook)
                self.assertEqual(sender.call_count, 1)
                sent = sender.call_args.args[1]
                self.assertIn("AFTER ACTION REPORT", str(sent))
                latest = json.loads((dest / "matches.json").read_text())["matches"][0]
                self.assertEqual(latest["winner"], "Lonestar")
                self.assertTrue(latest["winnerVerified"])
                self.assertEqual(json.loads((dest / "delivery.json").read_text())
                                 ["posted"]["9811"], "314159")

                recap.run(webhook=webhook)
                self.assertEqual(sender.call_count, 1)
                self.assertGreaterEqual(state["details"], 2)

    def test_disagreeing_detail_winner_remains_pending_until_corrected(self):
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp)
            (dest / "delivery.json").write_text(
                json.dumps({"initialized": True, "posted": {}}), encoding="utf-8")
            state = {"winner": "Valkyra"}

            def response(url, **kwargs):
                if "?page=" in url:
                    return {"ok": True, "matches": [{**SOURCE, "winner": "Lonestar"}], "pages": 1}
                if url.endswith("/9811"):
                    return {"ok": True, "match": {**SOURCE, "winner": state["winner"]},
                            "lines": [], "awards": []}
                if url == recap.PUBLIC_STATUS:
                    return {"ok": True, "server": {}}
                return {"ok": True, "players": [], "page": 1, "pages": 1}

            with patch.object(recap, "DATA", dest), \
                 patch.object(recap, "fetch_json", side_effect=response), \
                 patch.object(recap, "render_match_card", return_value=b"mock png"), \
                 patch.object(recap, "send_discord", return_value="8675309") as sender:
                recap.run(webhook="https://discord.com/api/webhooks/12345/validtoken")
                sender.assert_not_called()
                state["winner"] = "Lonestar"
                recap.run(webhook="https://discord.com/api/webhooks/12345/validtoken")
                sender.assert_called_once()

if __name__ == "__main__":
    unittest.main()
