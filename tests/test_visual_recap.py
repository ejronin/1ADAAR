import json
import unittest
from pathlib import Path
from unittest.mock import patch
from src.recap import discord_payload, send_discord
from src.recap_card import render_match_card
from src.discord_smoke import DEMO_MATCH, smoke_payload

ROOT = Path(__file__).resolve().parents[1]

class VisualRecapTest(unittest.TestCase):
    def test_real_recaps_are_valid_png(self):
        sample={**DEMO_MATCH,"id":234,"awards":[]}
        img=render_match_card(sample)
        self.assertTrue(img.startswith(b"\x89PNG\r\n\x1a\n"))
        self.assertLess(len(img),7_000_000)
        self.assertIn("attachment://match-recap.png",json.dumps(discord_payload({
            **sample,"warconUrl":"https://console.warcon.app/s/demo/matches/234",
            "winner":"Lonestar","peakPlayers":32,"endedAt":"2026-10-16T20:10:00Z","verifiedCompleted":True,"winnerVerified":True
        })))
    def test_smoke_has_fictional_scores_and_watermark(self):
        self.assertEqual(DEMO_MATCH["id"],0)
        self.assertIn("TEST — NOT A REAL MATCH",smoke_payload()["components"][0]["components"][0]["content"])
        self.assertIn("FICTIONAL",json.dumps(smoke_payload()))
        self.assertGreater(len(render_match_card(DEMO_MATCH,demo=True)),10000)
    def test_multipart_contains_image_and_disables_pings(self):
        from unittest.mock import MagicMock
        from io import BytesIO
        class Response:
            headers={}
            def __enter__(self): return self
            def __exit__(self,*a):return False
            def read(self,*args):return b'{"id":"123456789"}'
        payload=smoke_payload()
        raw=render_match_card(DEMO_MATCH,demo=True)
        with patch("src.recap.urllib.request.urlopen",return_value=Response()) as mock:
            result=send_discord("https://discord.com/api/webhooks/123456/validtoken",payload,image_bytes=raw)
            request=mock.call_args.args[0]
            body=request.data
            self.assertEqual(result,"123456789")
            self.assertIn(b'files[0]',body)
            self.assertIn(b'payload_json',body)
            self.assertIn(b'match-recap.png',body)
            self.assertIn(b'"parse": []',body)
            self.assertIn(b'"flags": 32768',body)
            self.assertIn("with_components=true",request.full_url)
            self.assertIn(raw,body)
    def test_demo_is_not_part_of_live_data(self):
        fixture=json.loads((ROOT/"tests/fixtures/demo-player.json").read_text())
        players=json.loads((ROOT/"docs/data/players.json").read_text())
        matches=json.loads((ROOT/"docs/data/matches.json").read_text())
        self.assertTrue(fixture["fictional"])
        self.assertEqual(fixture["player"]["name"],"PlayerOne")
        self.assertNotIn("demo-playerone",json.dumps(players))
        self.assertNotIn("demo-playerone",json.dumps(matches))
        self.assertNotIn("SAMPLE PLAYER — MADE-UP STATS", (ROOT/"docs/players.html").read_text())
        self.assertNotIn("id=\"view-demo\"", (ROOT/"docs/players.html").read_text())
