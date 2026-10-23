"""Checks for readable, plain-English, source-accurate 1ADAAR pages.

These contract checks are not a substitute for mobile screenshot or browser QA.
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

    def test_styles_have_clear_ownership_without_redundant_overlay(self):
        for filename in ("index.html", "players.html"):
            html = (ROOT / filename).read_text(encoding="utf-8")
            parser = PageInspector()
            parser.feed(html)
            styles = [x["href"] for x in parser.links if x.get("rel") == "stylesheet"]
            self.assertEqual(styles[0], "assets/style.css", filename)
            self.assertTrue(styles[1].startswith("assets/brand.css?"), filename)
            self.assertFalse(any("polish.css" in x for x in styles), filename)
            for stylesheet in styles:
                self.assertTrue((ROOT / stylesheet.split("?")[0]).is_file(), stylesheet)

    def test_skip_navigation_and_one_page_heading(self):
        for filename, _, parser in self.pages():
            self.assertEqual(parser.skip_links, ["#content"], filename)
            self.assertIn("content", parser.ids, filename)
            self.assertEqual(parser.headings, ["h1"], filename)

    def test_branded_share_preview_does_not_expose_personal_details(self):
        for filename, _, parser in self.pages():
            for key in ("og:type", "og:site_name", "og:title", "og:description", "og:image", "og:image:alt"):
                self.assertTrue(parser.meta.get(key), (filename, key))
            self.assertIn("wardogs-official-hero.webp", parser.meta["og:image"])
            self.assertNotIn("SteamID", parser.meta["og:description"])

    def test_plain_english_consistent_navigation_and_data_scope(self):
        for filename in ("index.html", "players.html", "playerone-demo.html"):
            html = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("Match history</a>", html, filename)
            self.assertIn("Find a player</a>", html, filename)
            self.assertIn(">MENU</div>", html, filename)
            self.assertNotIn("THE COMMAND DECK", html)
            self.assertNotIn(">PLAYER INTELLIGENCE</a>", html)  # Plain-English nav; bold hero is intentional
            self.assertNotIn("MATCH DOSSIER", html)
        index = (ROOT / "index.html").read_text(encoding="utf-8")
        players = (ROOT / "players.html").read_text(encoding="utf-8")
        app = (ROOT / "js" / "app.js").read_text(encoding="utf-8")
        self.assertIn("MATCHES. PLAYERS.",index)
        self.assertIn("RESULTS.",index)
        self.assertIn("latest 120 matches we have saved", index)
        self.assertIn("may not include every match played", index)
        self.assertIn("older matches may be missing", players)
        self.assertNotIn("A clearer story.", index)  # Reject retired generic marketing copy
        self.assertIn("Match history saved", app)
        self.assertIn("VIEW MATCH", app)
        self.assertNotIn("VIEW DOSSIER", app)

    def test_readable_controls_reduced_motion_and_clear_status(self):
        brand = (ROOT / "assets" / "brand.css").read_text(encoding="utf-8")
        server = (ROOT / "assets" / "server-status.css").read_text(encoding="utf-8")
        players = (ROOT / "assets" / "players.css").read_text(encoding="utf-8")
        perf = (ROOT / "assets" / "performance.css").read_text(encoding="utf-8")
        for fragment in ("@media(prefers-reduced-motion:reduce)", "@media(max-width:380px)",
                         "hero::after", ".rail .nav", "font-size:13.5px"):
            self.assertIn(fragment, brand)
        self.assertIn('server-status[data-state="offline"]', server)
        self.assertIn("animation:none", server)
        self.assertIn(".metric-tile span", players)
        self.assertIn(".perf-tab{font-size:12.5px", perf)
        status = (ROOT / "js" / "server-status.js").read_text(encoding="utf-8")
        self.assertIn("STATUS UNKNOWN", status)
        self.assertNotIn("STATUS UNAVAILABLE", status)


if __name__ == "__main__":
    unittest.main()
