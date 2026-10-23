import json
import unittest
from pathlib import Path

class DemoPageTests(unittest.TestCase):
    def test_retired_demo_only_exists_as_internal_fixture(self):
        root=Path(__file__).resolve().parents[1]/'docs'
        live=(root/'players.html').read_text()
        demo=((Path(__file__).resolve().parents[1]/'tests/fixtures/playerone-demo.html')).read_text()
        self.assertNotIn('href="playerone-demo.html"',live)
        self.assertNotIn('id="view-demo" class="demo-button" type="button"',live)
        self.assertIn('SAMPLE PLAYER — MADE-UP STATS',demo)
        self.assertIn('SAMPLE PLAYER / MADE-UP STATS',demo)
        self.assertNotIn('src="js/players.js"',demo)
        self.assertNotIn('data/players.json',demo)
        self.assertNotIn('steamcommunity.com',demo)
    def test_demo_page_consistent_with_separate_fixture(self):
        root=Path(__file__).resolve().parents[1]/'docs'
        fixture=json.loads(((Path(__file__).resolve().parents[1]/'tests/fixtures/demo-player.json')).read_text())
        page=(Path(__file__).resolve().parents[1]/'tests/fixtures/playerone-demo.html').read_text()
        self.assertTrue(fixture['fictional'])
        self.assertEqual(fixture['player']['name'],'PlayerOne')
        self.assertIn(str(fixture['player']['kills']),page)
        self.assertIn(str(fixture['player']['deaths']),page)
        self.assertIn(f"{fixture['player']['kills']/fixture['player']['deaths']:.2f}",page)
        for name in ('Bakurani','Ozeti','Zestafona','Lonestar','Valkyra','Manticore'):
            self.assertIn(name,page)
        self.assertEqual(page.count('<tr>'),11)  # Only latest ten fictional matches shown in compact table
        self.assertEqual(len(fixture['matches']),32)
    def test_demo_is_not_in_production_public_player_index(self):
        root=Path(__file__).resolve().parents[1]/'docs'
        players=json.loads((root/'data/players.json').read_text())
        matches=json.loads((root/'data/matches.json').read_text())
        self.assertNotIn('demo-playerone',json.dumps(players))
        self.assertNotIn('demo-playerone',json.dumps(matches))
