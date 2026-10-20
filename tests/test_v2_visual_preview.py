"""Visual preview must be isolated from production data and clearly marked demo."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PREVIEW = ROOT / "docs" / "v2-preview"


class VisualPreviewSafetyTests(unittest.TestCase):
    def test_preview_is_isolated_and_marked_fictional(self):
        page = (PREVIEW / "index.html").read_text(encoding="utf-8")
        self.assertIn("V2.0 DESIGN PREVIEW", page)
        self.assertIn("fictional examples", page)
        self.assertIn("Nothing here comes from a real player", page)
        self.assertIn('href="../index.html"', page)
        self.assertIn("Open live v1.0.1", page)
        self.assertIn("SAMPLE DATA", page)
        for name in ("profile", "maps", "weekly"):
            self.assertIn('id="view-' + name + '"', page)
            self.assertIn('data-target="' + name + '"', page)
        for asset in ("../assets/1ad-logo.svg", "../assets/wardogs-fullmark.png",
                      "../assets/factions/lonestar.svg",
                      "../assets/factions/valkyra.svg",
                      "../assets/factions/manticore.svg"):
            self.assertIn(asset, page)
            self.assertTrue((PREVIEW / asset).is_file(), asset)
        self.assertIn('src="preview.js?v=1"', page)
        self.assertIn('href="preview.css?v=1"', page)

    def test_js_only_uses_demonstration_records(self):
        js = (PREVIEW / "preview.js").read_text(encoding="utf-8")
        self.assertIn("Every number and name is fictional", js)
        self.assertNotIn("fetch(", js)
        self.assertNotIn("XMLHttpRequest", js)
        self.assertNotIn("innerHTML", js)
        self.assertNotIn("steamId", js)
        self.assertNotIn("discord.com", js.lower())
        self.assertIn("data-target", js)
        self.assertIn("combo-map", js)
        self.assertIn("combo-team", js)

    def test_visuals_are_responsive_and_accessible(self):
        html = (PREVIEW / "index.html").read_text(encoding="utf-8")
        css = (PREVIEW / "preview.css").read_text(encoding="utf-8")
        self.assertIn('aria-pressed="true"', html)
        self.assertIn('role="img"', html)
        self.assertIn('aria-label=', html)
        self.assertIn('@media(max-width:680px)', css)
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn(':focus-visible', css)
        self.assertIn('conic-gradient', css)
        self.assertIn('.podium', css)


if __name__ == "__main__":
    unittest.main()
