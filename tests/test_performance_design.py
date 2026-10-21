import unittest
from pathlib import Path
import json

DOCS=Path(__file__).resolve().parents[1]/"docs"

class PerformanceDesignTests(unittest.TestCase):
    def test_player_and_demo_share_accessible_design(self):
        for name in ("players.html","playerone-demo.html"):
            text=(DOCS/name).read_text(encoding="utf-8")
            self.assertIn('id="performance-module"',text)
            self.assertIn('src="js/performance-core.js?v=1"',text)
            self.assertIn('src="js/performance.js?v=5"',text)
            self.assertIn('assets/performance.css?v=4"',text)
            self.assertIn('MAP AND FACTION PERFORMANCE',text)
            self.assertIn('href="activity.html"',text)
            self.assertIn('class="profile-activity-link"',text)
            self.assertIn('Recent completed matches',text)
            self.assertIn('assets/player-v11.css?v=1',text)
            self.assertIn('id="player-snapshot"',text)
            self.assertIn('id="profile-secondary"',text)
        live=(DOCS/"js/players.js").read_text()
        self.assertIn("data/history/",live)
        self.assertIn("window.OneADAARPerformance.mount",live)
        self.assertIn("publicState.selected?.key!==entry.key",live)
    def test_fictional_timeline_has_internal_consistency(self):
        fixture=json.loads((DOCS/"data/demo-player.json").read_text())
        self.assertTrue(fixture["fictional"])
        self.assertEqual(len(fixture["matches"]),32)
        self.assertEqual(len(fixture["careerHistory"]),32)
        self.assertEqual(fixture["careerHistory"][-1]["kills"],fixture["player"]["kills"])
        self.assertEqual(fixture["careerHistory"][-1]["deaths"],fixture["player"]["deaths"])
        self.assertEqual(fixture["careerHistory"][-1]["matches"],fixture["player"]["matches"])
        self.assertEqual((DOCS/"playerone-demo.html").read_text().count("<tr>"),11)
        self.assertEqual(fixture["matches"][0]["endedAt"],"2026-10-15T19:00:00Z")
        self.assertEqual(fixture["careerHistory"][0]["matches"],17)
        self.assertTrue(all(b["matches"]==a["matches"]+1 for a,b in
            zip(fixture["careerHistory"],fixture["careerHistory"][1:])))
        self.assertNotIn("demo-playerone",(DOCS/"data/players.json").read_text())
        javascript=(DOCS/"js/demo-performance.js").read_text()
        self.assertIn("demo:true",javascript)
        self.assertNotIn("fetch(",javascript)
        self.assertNotIn("steamId",javascript)
    def test_no_fake_stats_in_production(self):
        for filename in ("data/players.json","data/matches.json"):
            self.assertNotIn("demo-playerone",(DOCS/filename).read_text())
    def test_keyboard_svg_and_mobile_css(self):
        css=(DOCS/"assets/performance.css").read_text()
        js=(DOCS/"js/performance.js").read_text()
        self.assertIn("@media(max-width:720px)",css)
        self.assertIn("prefers-reduced-motion",css)
        self.assertIn("role:'img'",js)
        self.assertIn("'aria-label'",js)
        self.assertIn("perf-details",js)
        self.assertIn("aria-pressed",js)
        self.assertIn("tabindex:'0'",js)
