"""Homepage live-map feature contract: validated WARCON state drives actual map art."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'

class HomepageCurrentMapTests(unittest.TestCase):
    def test_live_map_gets_wide_card_and_hero_status_link(self):
        html=(DOCS/'index.html').read_text()
        self.assertIn('class="server-status-cell server-status-players-tile"',html)
        self.assertIn('class="server-status-cell server-status-map-tile"',html)
        self.assertIn('class="secondary hero-warcon-status"',html)
        self.assertNotIn('class="server-status-source"',html)
        self.assertIn('assets/server-map-feature.css?v=118',html)
        self.assertIn('js/server-status.js?v=118',html)
        css=(DOCS/'assets/server-map-feature.css').read_text()
        self.assertIn('minmax(335px,1.65fr)',css)
        self.assertIn('.server-status-map-tile.map-banner-present',css)
        self.assertIn('background-position:center center',css)
        script=(DOCS/'js/server-status.js').read_text()
        self.assertIn("if(online&&doc.map&&mapTile)",script)
        self.assertIn("OneADAARMapBanners?.decorateMapRow",script)
        self.assertIn("doc.map.slice(0,55):'—'",script)

if __name__=='__main__':
    unittest.main()
