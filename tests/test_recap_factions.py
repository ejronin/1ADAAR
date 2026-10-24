import io
import unittest
from pathlib import Path
from PIL import Image
from src.recap_card import render_match_card, faction_color, faction_emblem
from src.discord_smoke import DEMO_MATCH
from src.recap import discord_payload

ROOT=Path(__file__).resolve().parents[1]
class FactionRecapArtworkTests(unittest.TestCase):
    def test_faction_emblem_is_actual_svg_based_and_local(self):
        for name,color in (("lonestar","#465eff"),("valkyra","#ee4138"),("manticore","#3eba42")):
            svg=(ROOT/"docs/assets/factions"/f"{name}.svg")
            self.assertTrue(svg.is_file())
            self.assertEqual(faction_color(name.upper()),color)
            icon=faction_emblem(name)
            self.assertEqual(icon.mode,"RGBA")
            self.assertEqual(icon.size,(52,52))
            self.assertGreater(icon.getbbox()[2]-icon.getbbox()[0],20)
        self.assertIsNone(faction_color("OtherFaction"))
    def test_real_recap_uses_faction_by_name_even_when_score_rows_reordered(self):
        def make(scores):
            return {**DEMO_MATCH,"id":127,"winner":"Valkyra","scores":scores,"awards":[]}
        scores=[{"name":"Valkyra","score":100},{"name":"Lonestar","score":77},{"name":"Manticore","score":39}]
        raw=render_match_card(make(scores))
        with Image.open(io.BytesIO(raw)) as im:
            self.assertEqual(im.mode,"RGB")
            self.assertEqual(im.size[0],1080)
            # v1.1 redesigned scoreboard: bar runs under each factual faction row.
            self.assertEqual(im.getpixel((140,549)),(238,65,56))
            self.assertEqual(im.getpixel((140,631)),(70,94,255))
            self.assertEqual(im.getpixel((140,713)),(62,186,66))
            self.assertEqual(im.size[1],816)
        self.assertEqual(discord_payload({
            **make(scores),"warconUrl":"https://console.warcon.app/s/demo/matches/127",
            "peakPlayers":32,"endedAt":"2026-10-16T20:10:00Z","verifiedCompleted":True,"winnerVerified":True
        })["components"][0]["accent_color"],0xEE4138)
    def test_unknown_faction_does_not_get_invented_emblem(self):
        self.assertIsNone(faction_color("NewFaction"))
        raw=render_match_card({**DEMO_MATCH,"winner":"Draw",
            "scores":[{"name":"NewFaction","score":100}],"awards":[]},demo=True)
        self.assertTrue(raw.startswith(b"\x89PNG\r\n\x1a\n"))
