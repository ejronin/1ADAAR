"""Regression checks for the public 1ADAAR brand shell; no network needed."""
from pathlib import Path
from html.parser import HTMLParser
import unittest
import xml.etree.ElementTree as ET

DOCS = Path(__file__).resolve().parents[1] / "docs"


class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.assets = []
        self.logo_count = 0
        self.discord_cta = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "img" and a.get("src", "").startswith("assets/"):
            self.assets.append(a["src"])
            if a["src"] == "assets/1ad-logo.svg":
                self.logo_count += 1
        if tag == "link" and a.get("href", "").startswith("assets/"):
            self.assets.append(a["href"])
        if tag == "a" and "discord.gg/e9B69UkE53" in a.get("href", ""):
            self.discord_cta += 1


class TestBranding(unittest.TestCase):
    def test_no_fake_logo_and_official_mark_used_twice(self):
        page = (DOCS / "index.html").read_text(encoding="utf-8")
        parsed = AssetParser()
        parsed.feed(page)
        self.assertGreaterEqual(parsed.logo_count, 2)
        self.assertNotIn('<div class="hero-number">1AD</div>', page)
        self.assertNotIn('<div class="brandmark"', page)
        self.assertGreaterEqual(parsed.discord_cta, 1)

    def test_all_local_assets_exist_and_svgs_parse(self):
        parsed = AssetParser()
        parsed.feed((DOCS / "index.html").read_text(encoding="utf-8"))
        for asset in parsed.assets + ["assets/tactical-terrain.svg", "assets/discord.svg"]:
            full = DOCS / asset
            self.assertTrue(full.is_file(), asset)
            if full.suffix == ".svg":
                self.assertEqual(ET.parse(full).getroot().tag.rsplit('}', 1)[-1], "svg")

    def test_brand_styles_are_responsive_and_accessible(self):
        css = (DOCS / "assets/brand.css").read_text(encoding="utf-8")
        self.assertIn("@media(max-width:720px)", css)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("#56ce71", css)


if __name__ == "__main__":
    unittest.main()
