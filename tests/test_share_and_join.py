import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]/'docs'

class ShareAndJoinTests(unittest.TestCase):
    def test_contextual_onboarding_does_not_add_sidebar_item(self):
        html=(ROOT/'index.html').read_text()
        self.assertIn('<section id="join-wardogs"', html)
        self.assertIn('New to WARDOGS?', html)
        self.assertIn('grab the server join code in Discord', html)
        self.assertEqual(html.count('href="https://discord.gg/e9B69UkE53"'),2)
        sidebar=html.split('<aside class="rail"',1)[1].split('</aside>',1)[0]
        self.assertNotIn('join-wardogs',sidebar)
    def test_match_share_is_for_actual_opened_match_only(self):
        html=(ROOT/'index.html').read_text()
        js=(ROOT/'js/app.js').read_text()
        self.assertIn('id="share-match"',html)
        self.assertIn('id="match-share-status"',html)
        self.assertIn('state.currentMatch=m',js)
        self.assertIn("if(!state.currentMatch)return",js)
        self.assertIn('index.html#match-',js)
        self.assertIn('window.OneADAARShare.share(',js)
    def test_player_share_does_not_use_raw_steamid(self):
        html=(ROOT/'players.html').read_text()
        js=(ROOT/'js/players.js').read_text()
        self.assertIn('id="share-player"',html)
        self.assertIn('id="player-share-status"',html)
        self.assertIn('players.html#player-',js)
        self.assertIn('^[a-f0-9]{64}$',js)
        self.assertNotIn('steamcommunity.com',js)
    def test_playerone_demo_share_labels_fictional(self):
        html=(ROOT/'playerone-demo.html').read_text()
        js=(ROOT/'js/demo-share.js').read_text()
        self.assertIn('id="share-demo"',html)
        self.assertIn('demo-share-status',html)
        self.assertIn('fictional stats',js)
    def test_fallback_link_without_clipboard_dependency(self):
        share=(ROOT/'js/share.js').read_text()
        self.assertIn('navigator.share',share)
        self.assertIn('navigator.clipboard.writeText',share)
        self.assertIn('input.select()',share)
        self.assertIn('destination.origin !== location.origin',share)
