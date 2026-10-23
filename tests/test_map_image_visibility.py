"""Map images must appear even when WARCON has zero saved completed matches."""
from pathlib import Path
from html.parser import HTMLParser
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/"docs"
NAMES=("bakurani","ozeti","zestafona")

class MapImages(HTMLParser):
    def __init__(self):
        super().__init__(); self.images=[]
    def handle_starttag(self,tag,attrs):
        item=dict(attrs)
        if tag=="img" and "map-banners/" in item.get("src",""):
            self.images.append(item)

class MapArtTests(unittest.TestCase):
    def test_named_images_exist_and_are_in_live_pages(self):
        for name in NAMES:
            path=DOCS/"assets"/"map-banners"/(name+"-card.webp")
            self.assertTrue(path.is_file(),path)
        for page in ("index.html","map-team.html"):
            html=(DOCS/page).read_text(encoding="utf-8")
            self.assertIn('id="map-art-heading"',html)
            self.assertIn("assets/map-gallery.css?v=117",html)
            self.assertIn("js/map-banners.js?v=117",html)
            reader=MapImages();reader.feed(html)
            images=reader.images
            self.assertEqual(len(images),3,page)
            for name in NAMES:
                self.assertTrue(any(
                    x["src"]=="assets/map-banners/"+name+"-card.webp?v=117"
                    and name.capitalize() in x.get("alt","") for x in images
                ),(page,name))
        # The section is static HTML, not inside a match-results conditional.
        self.assertIn('class="map-art-section"',(DOCS/"index.html").read_text())

    def test_css_variable_images_resolve_against_page_not_stylesheet(self):
        js=(DOCS/"js"/"map-banners.js").read_text()
        self.assertIn("new URL('assets/map-banners/',document.baseURI)",js)
        self.assertIn("new URL(file,galleryBase).href",js)
        self.assertIn("'--map-banner'",js)
        self.assertIn("testImage.onerror",js)
        self.assertIn("dataset.mapBanner",js)
        self.assertNotIn("'url(\"'+base+file",js)
        status=(DOCS/"js"/"server-status.js").read_text()
        self.assertIn("delete mapTile.dataset.mapBanner",status)

if __name__=="__main__":
    unittest.main()
