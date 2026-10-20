"""v2 captured-history browser: files are local public data and strictly labeled."""
import unittest
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]


class SeasonBrowserTests(unittest.TestCase):
    def test_empty_manifest_is_honest_and_has_no_sample_matches(self):
        index=json.loads((ROOT/"docs/data/seasons/index.json").read_text())
        self.assertEqual(index["schemaVersion"],1)
        self.assertEqual(index["coverage"],"captured-only")
        self.assertEqual(index["seasons"],[])
        self.assertNotIn("playerone",json.dumps(index).lower())
        html=(ROOT/"docs/seasons.html").read_text()
        self.assertIn("not a complete record of every match played",html)
        self.assertIn('id="season-message"',html)
        self.assertIn('id="season-more"',html)
        self.assertIn('id="season-filter"',html)
        self.assertIn('src="js/seasons.js?v=1"',html)
        self.assertIn('href="assets/seasons.css?v=1"',html)

    def test_no_private_requests_or_synthetic_match_data(self):
        js=(ROOT/"docs/js/seasons.js").read_text()
        self.assertIn("data/seasons/index.json",js)
        self.assertIn("'data/seasons/'+s.seasonKey+'/'+selected.month+'.json'",js)
        self.assertIn("WARCON",js)
        self.assertNotIn("steamId",js)
        self.assertNotIn("innerHTML",js)
        self.assertNotIn("demo-playerone",js)
        self.assertNotIn("authorization",js.lower())
        self.assertIn("more.addEventListener('click',renderNext)",js)

    def test_all_pages_link_to_older_matches(self):
        for name in ("index.html", "players.html", "playerone-demo.html",
                     "weekly.html", "compare.html"):
            html=(ROOT/"docs"/name).read_text()
            self.assertIn('href="seasons.html"',html,name)
        css=(ROOT/"docs/assets/seasons.css").read_text()
        self.assertIn("@media(max-width:760px)",css)
        self.assertIn("focus-visible",css)


if __name__=="__main__":
    unittest.main()
