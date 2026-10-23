"""v2 player comparison uses genuine public all-time WARCON data only."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class ComparePageContractTests(unittest.TestCase):
    def test_real_data_only_and_privacy(self):
        html = (ROOT/"docs/compare.html").read_text()
        js = (ROOT/"docs/js/compare.js").read_text()
        self.assertIn('src="js/compare.js?v=1"', html)
        self.assertIn('href="assets/compare.css?v=1"', html)
        self.assertIn("data/players.json", js)
        self.assertIn("all-time WARCON", html)
        self.assertIn("not current-season", html)
        self.assertIn("keyPattern=/^[a-f0-9]{64}$/", js)
        self.assertIn("textContent", js)
        self.assertNotIn("steamcommunity.com", html+js)
        self.assertNotIn("demo-playerone", html+js)
        self.assertNotIn("SteamID64", html+js)
        self.assertNotIn("7656119", html+js)
        self.assertNotIn("innerHTML", js)

    def test_controls_and_accessibility(self):
        html=(ROOT/"docs/compare.html").read_text()
        for value in ('<main id="content"', 'id="compare-first"', 'id="compare-second"',
                      'id="compare-rows"', 'id="compare-message"', 'id="compare-form"',
                      'id="compare-copy"', 'id="compare-share-feedback"',
                      'aria-live="polite"', 'role="region"', 'aria-current="page"'):
            self.assertIn(value, html)
        css=(ROOT/"docs/assets/compare.css").read_text()
        self.assertIn("@media(max-width:780px)",css)
        self.assertIn("min-height:51px",css)
        self.assertIn(":focus-visible",css)

    def test_plain_english_nav_from_existing_pages(self):
        for name in ("index.html", "players.html", "weekly.html"):
            body=(ROOT/"docs"/name).read_text()
            self.assertIn('href="compare.html"',body,name)
            self.assertIn("Compare players</a>",body,name)


if __name__=="__main__":
    unittest.main()
