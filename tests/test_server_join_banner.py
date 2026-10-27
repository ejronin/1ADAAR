"""Home-page join-ID overlay, QR landing and copy controls."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
CODE='a071b4aa-9574-4e7d-858c-0da3bea80f52'

class JoinBannerContracts(unittest.TestCase):
    def test_same_server_artwork_name_and_semantic_copy_control(self):
        home=(DOCS/'index.html').read_text()
        join=(DOCS/'join.html').read_text()
        self.assertIn('class="hero motion-hero server-banner-hero"',home)
        self.assertIn('class="server-banner-media"',home)
        self.assertIn('class="server-banner-media"',join)
        for page in (home,join):
            self.assertIn('id="copy-server-join-code"',page)
            self.assertIn('id="server-join-copy-status"',page)
            self.assertIn('aria-live="polite"',page)
            self.assertIn('type="button"',page)
            self.assertEqual(page.count(CODE),2)
            self.assertIn('assets/server-join.css?v=114' if page is home else 'assets/server-join.css?v=115',page)
            self.assertIn('js/server-join.js?v=113',page)
        self.assertLess(home.index('class="hero-text server-banner-toolbar"'),home.index('class="server-join-overlay"'))
        self.assertGreater(home.index('class="server-join-overlay"'),home.index('class="server-banner-media"'))
        self.assertIn('.server-banner-hero .server-join-overlay{', (DOCS/'assets/server-join.css').read_text())
        self.assertIn('position:static!important;', (DOCS/'assets/server-join.css').read_text())
        self.assertIn('max-width:325px', (DOCS/'assets/server-join.css').read_text())
        self.assertIn('href="join.html"',home)
        self.assertEqual(home.count('Join the 1AD Discord'),1)
        self.assertEqual(home.count('discord.gg/e9B69UkE53'),1)
        css=(DOCS/'assets/server-join.css').read_text()
        self.assertIn("url('oneaveragedan-server-banner.png?v=113')",css)
        self.assertIn('aspect-ratio:4 / 1',css)
        self.assertIn('background-position:center,center',css)

    def test_qr_landing_shows_dan_discord_invite_beside_join_code(self):
        html=(DOCS/'join.html').read_text()
        css=(DOCS/'assets/server-join.css').read_text()
        self.assertIn('class="join-discord-panel"',html)
        self.assertIn("Join Dan's Discord",html)
        self.assertIn('aria-label="Join Dan\'s Discord community (opens in a new tab)"',html)
        self.assertIn('href="https://discord.gg/e9B69UkE53"',html)
        self.assertEqual(html.count('https://discord.gg/e9B69UkE53'),1)
        self.assertLess(html.index('id="copy-server-join-code"'),
                        html.index('class="join-discord-panel"'))
        self.assertLess(html.index('class="join-discord-panel"'),
                        html.index('id="join-steps"'))
        self.assertIn('rel="noopener noreferrer"',html)
        self.assertIn('.join-landing .join-discord-link:focus-visible',css)
        self.assertIn('min-height:52px',css)

    def test_game_join_never_claims_browser_auto_launch(self):
        html=(DOCS/'join.html').read_text()
        for label in ('Deploy','Server Browser','Community','Join by ID','Lookup','Join Match'):
            self.assertIn(label,html)
        self.assertIn('cannot directly join the match',html)
        js=(DOCS/'js/server-join.js').read_text()
        self.assertIn('navigator.clipboard.writeText(CODE)',js)
        self.assertIn('document.execCommand',js)
        self.assertIn('COPY BLOCKED',js)
        self.assertNotIn('steam://',js)
        self.assertNotIn('eval(',js)

if __name__=='__main__': unittest.main()
