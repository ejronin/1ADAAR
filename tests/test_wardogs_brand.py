import unittest
from pathlib import Path

class TestWardogsBrand(unittest.TestCase):
    def test_official_wordmark_present_on_both_pages(self):
        root=Path(__file__).resolve().parents[1]/"docs"
        for name in ("index.html","players.html"):
            page=(root/name).read_text(encoding="utf-8")
            with self.subTest(page=name):
                self.assertIn('assets/wardogs-fullmark.png',page)
                self.assertIn('WARDOGS — Tactical All Out Warfare',page)
        self.assertTrue((root/"assets"/"wardogs-fullmark.png").exists())
