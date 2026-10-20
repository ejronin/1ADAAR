import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/'docs'

class NavigationAccessibilityTests(unittest.TestCase):
    def test_only_discord_and_real_latest_match_ctas(self):
        html=(ROOT/'index.html').read_text(encoding='utf-8')
        self.assertNotIn('Explore match reports',html)
        self.assertNotIn('Find your stats →',html)
        self.assertIn('id="latest-match-link"',html)
        self.assertIn('hidden aria-label="Open latest completed match details"',html)
        self.assertEqual(html.count('Join the 1AD Discord'),2)  # Existing hero CTA + onboarding
    def test_live_latest_match_link_activated_only_after_data_loaded(self):
        js=(ROOT/'js/app.js').read_text(encoding='utf-8')
        self.assertIn("if(data.matches.length){",js)
        self.assertIn("latestLink.hidden=false",js)
        self.assertIn("latestLink.onclick=event=>",js)
        self.assertIn("const id=/^#match-",js)
    def test_mobile_navigation_and_dialog_not_hidden(self):
        css=(ROOT/'assets/brand.css').read_text(encoding='utf-8')
        self.assertIn('.rail .nav,.rail .nav:not(.active){display:flex',css)
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',css)
        self.assertIn('.detail table{min-width:480px}',css)
        self.assertIn('#latest-match-link[hidden]{display:none!important}',css)
        for filename in ('index.html','players.html','playerone-demo.html'):
            page=(ROOT/filename).read_text(encoding='utf-8')
            self.assertIn('Match history</a>',page)
            self.assertIn('Find a player</a>',page)
    def test_player_dossiers_have_mobile_table_scrolling(self):
        css=(ROOT/'assets/players.css').read_text(encoding='utf-8')
        self.assertIn('.recent-table{min-width:540px}',css)
        self.assertIn('.table-scroll{overflow-x:auto',css)
