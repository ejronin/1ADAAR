"""Named WARDOGS images appear on actual live-map and recorded match tiles."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/"docs"
NAMES=("bakurani","ozeti","zestafona")

class MapArtTests(unittest.TestCase):
    def test_approved_art_is_present_without_unrelated_static_galleries(self):
        for name in NAMES:
            path=DOCS/"assets"/"map-banners"/(name+"-card.webp")
            self.assertTrue(path.is_file(),path)
            self.assertGreater(path.stat().st_size,10000)
        for page in ("index.html","map-team.html"):
            html=(DOCS/page).read_text(encoding="utf-8")
            self.assertNotIn('class="map-art-section"',html)
            self.assertNotIn("assets/map-gallery.css",html)
            self.assertIn("js/map-banners.js?v=117",html)
        home=(DOCS/"index.html").read_text()
        self.assertIn('class="server-status-cell server-status-map-tile"',home)
        self.assertIn("js/server-status.js?v=118",home)

    def test_css_variable_images_resolve_against_page_not_stylesheet(self):
        js=(DOCS/"js"/"map-banners.js").read_text()
        self.assertIn("new URL('assets/map-banners/',document.baseURI)",js)
        self.assertIn("new URL(file,galleryBase).href",js)
        self.assertIn("'--map-banner'",js)
        self.assertIn("testImage.onerror",js)
        self.assertIn("dataset.mapBanner",js)
        status=(DOCS/"js"/"server-status.js").read_text()
        self.assertIn("delete mapTile.dataset.mapBanner",status)
        self.assertIn("if(online&&doc.map&&mapTile)",status)
        self.assertIn("decorateMapRow(mapTile,doc.map)",status)
        self.assertIn("OneADAARMapBanners?.decorateMapRow",(DOCS/"js"/"app.js").read_text())
        self.assertIn("OneADAARMapBanners.decorateMapRow",(DOCS/"js"/"map-team.js").read_text())

if __name__=="__main__":
    unittest.main()
