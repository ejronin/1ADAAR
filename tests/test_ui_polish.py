"""Contract checks for the v1.0.1 responsive visual/IA pass.

No external browser, WARCON access or paid service is required.
These are static safeguards, not a substitute for mobile screenshot acceptance.
"""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1] / "docs"


class PageInspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.headings = []
        self.meta = {}
        self.skip_links = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "link":
            self.links.append(a)
        if tag == "meta":
            self.meta[a.get("property") or a.get("name")] = a.get("content")
        if tag == "h1":
            self.headings.append("h1")
        if tag == "a" and a.get("class") == "skip":
            self.skip_links.append(a.get("href"))


class LaunchUXContractTests(unittest.TestCase):
    def pages(self):
        for filename in ("index.html", "players.html"):
            html = (ROOT / filename).read_text(encoding="utf-8")
            parser = PageInspector()
            parser.feed(html)
            yield filename, html, parser

    def test_shared_polish_layer_loaded_last(self):
        for filename, html, parser in self.pages():
            styles = [x["href"] for x in parser.links if x.get("rel") == "stylesheet"]
            self.assertTrue(styles[-1].startswith("assets/polish.css?"), filename)
            for stylesheet in styles:
                self.assertTrue((ROOT / stylesheet.split("?")[0]).is_file(), stylesheet)

    def test_nav_skip_and_landmarks(self):
        for filename, _, parser in self.pages():
            self.assertEqual(parser.skip_links, ["#content"], filename)
            self.assertIn("content", parser.ids, filename)
            self.assertEqual(parser.headings, ["h1"], filename)

    def test_community_social_preview_is_generic_not_player_personal(self):
        for filename, _, parser in self.pages():
            for key in ("og:type", "og:site_name", "og:title", "og:description", "og:image", "og:image:alt"):
                self.assertTrue(parser.meta.get(key), (filename, key))
            self.assertIn("wardogs-official-hero.webp", parser.meta["og:image"])
            self.assertNotIn("SteamID", parser.meta["og:description"])

    def test_limit_and_provenance_copy_not_misleading(self):
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        app = (ROOT / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("latest 120 captured reports", index)
        self.assertNotIn("Every match.", index)
        self.assertIn("Archive updated", app)
        self.assertNotIn("?'SYNCED':'AWAITING DATA'", app)

    def test_motion_readability_and_status_safety(self):
        style = (ROOT / "assets" / "polish.css").read_text(encoding="utf-8")
        for required in (
            "@media(prefers-reduced-motion:reduce)",
            "@media(max-width:380px)",
            "hero::after",
            "server-status[data-state=\"offline\"]",
            ".rail .nav",
            ".perf-tab",
        ):
            self.assertIn(required, style)
        self.assertIn("animation:none", style)
        status = (ROOT / "js" / "server-status.js").read_text(encoding="utf-8")
        self.assertIn("STATUS NOT VERIFIED", status)


if __name__ == "__main__":
    unittest.main()
