import json
import unittest
from pathlib import Path

class DemoPageTests(unittest.TestCase):
    def test_static_playerone_demo_is_regular_link_without_network_dependency(self):
        root=Path(__file__).resolve().parents[1]/'docs'
        live=(root/'players.html').read_text()
        demo=(root/'playerone-demo.html').read_text()
        self.assertIn('href="playerone-demo.html"',live)
        self.assertNotIn('id="view-demo" class="demo-button" type="button"',live)
        self.assertIn('DEMO PROFILE — FICTIONAL DATA',demo)
        self.assertIn('PLAYER INTELLIGENCE / SYNTHETIC DEMO DATA',demo)
        self.assertNotIn('src="js/players.js"',demo)
        self.assertNotIn('data/players.json',demo)
        self.assertNotIn('steamcommunity.com',demo)
    def test_demo_page_consistent_with_separate_fixture(self):
        root=Path(__file__).resolve().parents[1]/'docs'
        fixture=json.loads((root/'data/demo-player.json').read_text())
        page=(root/'playerone-demo.html').read_text()
        self.assertTrue(fixture['fictional'])
        self.assertEqual(fixture['player']['name'],'PlayerOne')
        self.assertIn(str(fixture['player']['kills']),page)
        self.assertIn(str(fixture['player']['deaths']),page)
        self.assertIn(f"{fixture['player']['kills']/fixture['player']['deaths']:.2f}",page)
        for name in ('Bakurani','Ozeti','Zestafona','Lonestar','Valkyra','Manticore'):
            self.assertIn(name,page)
        self.assertEqual(page.count('<tr>'),len(fixture['matches'])+1)
    def test_demo_is_not_in_production_public_player_index(self):
        root=Path(__file__).resolve().parents[1]/'docs'
        players=json.loads((root/'data/players.json').read_text())
        matches=json.loads((root/'data/matches.json').read_text())
        self.assertNotIn('demo-playerone',json.dumps(players))
        self.assertNotIn('demo-playerone',json.dumps(matches))
