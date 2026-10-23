"""Approved exact banner and 1ADAAR first-party text mark release gate."""
from pathlib import Path
import hashlib
import struct
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
PAGES=('index.html','seasons.html','players.html','map-team.html',
       'activity.html','progression.html','compare.html','weekly.html')
HASH='327dd32e079ade0c69eb4d9e7ebc13e09448d57adffbc96485c489032bbec8fc'

class ApprovedServerArtworkTests(unittest.TestCase):
    def test_exact_original_image_committed_and_not_an_alternative_render(self):
        path=DOCS/'assets/oneaveragedan-server-banner.png'
        raw=path.read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),HASH)
        self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n')
        self.assertEqual(struct.unpack('>II',raw[16:24]),(1024,256))
        self.assertLess(len(raw),1024*1024)

    def test_website_uses_exact_same_asset_not_a_second_mockup(self):
        css=(DOCS/'assets/server-join.css').read_text()
        js=(DOCS/'js/server-join.js').read_text()
        home=(DOCS/'index.html').read_text()
        join=(DOCS/'join.html').read_text()
        self.assertIn("url('oneaveragedan-server-banner.png?v=113')",css)
        self.assertIn("banner.src='assets/oneaveragedan-server-banner.png?v=113'",js)
        self.assertIn('server-banner-media',home)
        self.assertIn('server-banner-media',join)
        self.assertIn('id="copy-server-join-code"',home)
        self.assertIn('id="copy-server-join-code"',join)
        self.assertNotIn('a071b4aa-9574-4e7d-858c-0da3bea80f52',(DOCS/'assets/oneaveragedan-server-banner.png').read_bytes().decode('latin1',errors='ignore'))
        self.assertIn('https://ejronin.github.io/1ADAAR/assets/oneaveragedan-server-banner.png',home)
        self.assertIn('assets/oneaveragedan-server-banner.png?v=113',home)

    def test_wordmark_is_authentic_first_party_vector_on_every_active_page(self):
        wordmark=DOCS/'assets/1adaar-wordmark.svg'
        svg=wordmark.read_text()
        self.assertIn('1ADAAR',svg)
        self.assertIn('AFTER ACTION REPORT',svg)
        self.assertIn('<path',svg)
        self.assertIn('#70e795',svg)
        self.assertNotIn('@font-face',svg)
        for page in PAGES:
            with self.subTest(page=page):
                html=(DOCS/page).read_text()
                self.assertIn('src="assets/1adaar-wordmark.svg"',html)
                self.assertIn('src="assets/1ad-logo.svg"',html)
                self.assertIn('src="assets/wardogs-fullmark.png"',html)
                self.assertIn('href="index.html" aria-label="1ADAAR home"',html)
        join=(DOCS/'join.html').read_text()
        self.assertIn('class="join-site-wordmark"',join)
        self.assertIn('assets/wardogs-fullmark.png',join)

if __name__=='__main__':
    unittest.main()
