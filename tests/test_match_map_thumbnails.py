"""No persistent homepage map gallery. Recorded matches use small map thumbnails."""
from pathlib import Path
import unittest

DOCS=Path(__file__).resolve().parents[1]/"docs"

class MatchThumbTests(unittest.TestCase):
    def test_home_and_map_team_have_no_large_map_gallery(self):
        for page in ("index.html","map-team.html"):
            text=(DOCS/page).read_text()
            self.assertNotIn('class="map-art-grid"',text)
            self.assertNotIn('class="map-art-section"',text)
            self.assertNotIn('map-gallery.css',text)
        home=(DOCS/"index.html").read_text()
        self.assertIn('class="server-status-cell server-status-map-tile"',home)
        self.assertIn("assets/match-thumbnails.css?v=119",home)
        self.assertIn("js/app.js?v=119",home)

    def test_records_use_individual_thumbnails_not_full_card_background(self):
        script=(DOCS/"js/app.js").read_text()
        css=(DOCS/"assets/match-thumbnails.css").read_text()
        self.assertIn("OneADAARMapBanners?.resolveMap(m.map)",script)
        self.assertIn("assets/map-banners/",script)
        self.assertIn("match-map-thumb",script)
        self.assertIn("onerror",script)
        self.assertNotIn("decorateMapRow(btn,m.map)",script)
        self.assertIn("aspect-ratio:16/9",css)
        self.assertIn("background-image:none!important",css)

if __name__=="__main__":
    unittest.main()
