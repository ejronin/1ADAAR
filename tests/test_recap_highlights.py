"""Real PNG highlight cards: equal three-line hierarchy, source values, vector icons."""
import io
import unittest
from PIL import Image
from src.recap_card import render_match_card
from src.discord_smoke import DEMO_MATCH


class HighlightArtworkTests(unittest.TestCase):
    @staticmethod
    def fixture():
        awards = [
            {"key":"kills","label":"Most kills","name":"PlayerOne",
             "value":"38 kills","faction":"Lonestar"},
            {"key":"kd","label":"Best K/D","name":"PlayerTwo",
             "value":"4.20","faction":"Valkyra"},
            {"key":"longest","label":"Longest shot","name":"PlayerThree",
             "value":"527 m","faction":"Manticore"}
        ]
        return {**DEMO_MATCH, "awards": awards}

    def test_three_large_values_and_correct_known_faction_outlines(self):
        raw=render_match_card(self.fixture(),demo=True)
        with Image.open(io.BytesIO(raw)) as im:
            self.assertEqual(im.size,(1080,1036))
            self.assertEqual(im.mode,"RGB")
            for idx,outline in enumerate([(70,94,255),(238,65,56),(62,186,66)]):
                left=50+idx*330
                self.assertEqual(im.getpixel((left,875)),outline)
                # A dedicated high-contrast value row under icon/label/name:
                crop=im.crop((left+78,883,left+308,928)).convert("RGB")
                green=sum(1 for r,g,b in crop.getdata()
                          if 90<=r<=205 and g>=175 and b>=112)
                self.assertGreater(green,45,f"Card {idx} has no readable large numeric value")
                # Dedicated left 48px glyph region contains visible line art.
                glyph=im.crop((left+14,853,left+61,902)).convert("RGB")
                lit=sum(1 for r,g,b in glyph.getdata() if g>=160 and g>r+35)
                self.assertGreater(lit,20,f"Vector icon {idx} not visible")

    def test_missing_team_never_gets_fictional_faction_color(self):
        example=self.fixture()
        example["awards"][0].pop("faction")
        with Image.open(io.BytesIO(render_match_card(example,demo=True))) as im:
            self.assertEqual(im.getpixel((50,875)),(69,98,78))
            self.assertNotEqual(im.getpixel((50,875)),(70,94,255))

    def test_empty_awards_have_no_placeholder_cards(self):
        with Image.open(io.BytesIO(render_match_card({**DEMO_MATCH,
                                                      "awards":[]},demo=True))) as im:
            self.assertEqual(im.size,(1080,816))


if __name__=="__main__":
    unittest.main()
