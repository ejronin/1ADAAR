import unittest
from unittest.mock import patch
from src.discord_smoke import smoke_payload, main

class TestDiscordSmoke(unittest.TestCase):
    def test_payload_has_explicit_test_label_and_no_fake_scores(self):
        obj=smoke_payload()
        self.assertEqual(obj["allowed_mentions"], {"parse":[]})
        self.assertEqual(obj["flags"],32768)
        self.assertIn("TEST — NOT A REAL MATCH", obj["components"][0]["components"][0]["content"])
        self.assertIn("FICTIONAL",str(obj))
        self.assertNotIn("steamId", str(obj))
    def test_send_only_uses_existing_secret(self):
        with patch.dict("os.environ", {"DISCORD_MATCH_WEBHOOK":"https://discord.com/api/webhooks/123/abc"}), patch("src.discord_smoke.send_discord", return_value="1234") as sender:
            main()
            sender.assert_called_once()
            self.assertEqual(sender.call_args.args[0], "https://discord.com/api/webhooks/123/abc")
    def test_missing_secret_aborts(self):
        with patch.dict("os.environ", {"DISCORD_MATCH_WEBHOOK":""}), self.assertRaises(SystemExit):
            main()

if __name__=="__main__":
    unittest.main()
