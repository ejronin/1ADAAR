"""Only a guarded TEST can deliver fictional recap graphics to Discord."""
import unittest
from unittest.mock import patch
from src.discord_smoke import smoke_payload, weekly_smoke_payload, main

class TestDiscordSmoke(unittest.TestCase):
    def test_match_preview_has_explicit_test_label_and_button(self):
        obj=smoke_payload()
        self.assertEqual(obj["allowed_mentions"], {"parse":[]})
        self.assertEqual(obj["flags"],32768)
        self.assertIn("TEST — NOT A REAL MATCH", obj["components"][0]["components"][0]["content"])
        self.assertIn("FICTIONAL",str(obj))
        self.assertEqual(obj["components"][0]["components"][-1]["components"][0]["label"],"See full report")
        self.assertNotIn("steamId", str(obj))

    def test_weekly_preview_is_fictional_and_has_weekly_page_button(self):
        obj=weekly_smoke_payload()
        self.assertEqual(obj["flags"],32768)
        self.assertIn("WEEKLY ROUNDUP PREVIEW",str(obj))
        self.assertIn("FICTIONAL",str(obj))
        button=obj["components"][0]["components"][-1]["components"][0]
        self.assertEqual(button["label"],"See full report")
        self.assertEqual(button["url"],"https://ejronin.github.io/1ADAAR/weekly.html")

    def test_two_messages_use_same_existing_webhook_only(self):
        with patch.dict("os.environ", {"DISCORD_MATCH_WEBHOOK":"https://discord.com/api/webhooks/123/abc"}), \
             patch("src.discord_smoke.send_discord",side_effect=["1234","1235"]) as sender, \
             patch("src.discord_smoke.render_match_card",return_value=b"PNG"), \
             patch("src.discord_smoke.render_weekly_smoke_card",return_value=b"PNG"):
            main()
            self.assertEqual(sender.call_count,2)
            self.assertEqual({x.args[0] for x in sender.call_args_list},
                             {"https://discord.com/api/webhooks/123/abc"})

    def test_missing_secret_aborts_before_sending(self):
        with patch.dict("os.environ",{"DISCORD_MATCH_WEBHOOK":""}), self.assertRaises(SystemExit):
            main()

    def test_weekly_preview_png_contains_real_named_map_art(self):
        from src.discord_preview_cards import render_weekly_smoke_card
        png=render_weekly_smoke_card()
        self.assertTrue(png.startswith(b"\\x89PNG\\r\\n\\x1a\\n"))
        self.assertLess(len(png),7_000_000)

if __name__=="__main__":
    unittest.main()
