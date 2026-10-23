import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]/'docs'

class ShareAndJoinTests(unittest.TestCase):
    def test_contextual_onboarding_does_not_add_sidebar_item(self):
        html=(ROOT/'index.html').read_text()
        self.assertNotIn('<section id="join-wardogs"', html)
        self.assertIn('Join the 1AD Discord', html)
        self.assertIn('class="hero motion-hero"', html)
        self.assertEqual(html.count('href="https://discord.gg/e9B69UkE53"'),1)
        sidebar=html.split('<aside class="rail"',1)[1].split('</aside>',1)[0]
        self.assertNotIn('join-wardogs',sidebar)
        hero=html.split('<section class="hero motion-hero"',1)[1].split('</section>',1)[0]
        self.assertIn('Join the 1AD Discord',hero)
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
        html=((Path(__file__).resolve().parents[1]/'tests/fixtures/playerone-demo.html')).read_text()
        js=(ROOT/'js/demo-share.js').read_text()
        self.assertIn('id="share-demo"',html)
        self.assertIn('demo-share-status',html)
        self.assertIn('fictional stats',js)
    def test_fallback_link_without_clipboard_dependency(self):
        share=(ROOT/'js/share.js').read_text()
        self.assertIn('navigator.share',share)
        self.assertIn('navigator.clipboard.writeText',share)
        self.assertIn('input.select()',share)
        self.assertIn("document.createElement('textarea')",share)
        self.assertIn('destination.origin !== location.origin',share)

    def test_community_attribution_in_real_and_demo_profile_messages(self):
        players=(ROOT/'js/players.js').read_text()
        demo=(ROOT/'js/demo-share.js').read_text()
        for content in (players,demo):
            self.assertIn('OneAverageDan WARDOGS Community Server!',content)
            self.assertIn('Join the 1AD Discord: https://discord.gg/e9B69UkE53',content)
        self.assertIn('View my 1ADAAR player profile:',players)
        self.assertIn('DEMO',demo)
        self.assertNotIn('steamcommunity.com',players+demo)
        self.assertIn('players.html#player-',players)
