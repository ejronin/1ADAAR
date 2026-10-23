import unittest
from pathlib import Path
class WebsiteTests(unittest.TestCase):
    def test_phase2_assets_present(self):
        p=Path(__file__).resolve().parents[1]/'docs'
        for path in ['players.html','js/players.js','assets/players.css','assets/hero-battle.webp','data/players.json']:
            with self.subTest(path=path):self.assertTrue((p/path).is_file())
    def test_no_fake_numbers_or_steam_profile_links(self):
        p=Path(__file__).resolve().parents[1]/'docs'
        text=(p/'players.html').read_text()+ (p/'js/players.js').read_text()
        self.assertNotIn('2,847', text)
        self.assertNotIn('steamcommunity.com/profiles', text)
        self.assertNotIn('GRID // 1AD', (p/'index.html').read_text())
        self.assertNotIn('pill-link discord-link', (p/'index.html').read_text())
    def test_authentic_wardogs_hero(self):
        p=Path(__file__).resolve().parents[1]/'docs'
        self.assertTrue((p/'assets'/'wardogs-official-hero.webp').is_file())
        self.assertIn('wardogs-official-hero.webp',(p/'assets'/'brand.css').read_text())
    def test_official_logo_and_single_discord_link_in_hero(self):
        p=Path(__file__).resolve().parents[1]/'docs'
        s=(p/'index.html').read_text()
        self.assertIn('1ad-logo.svg',s)
        self.assertEqual(s.count('Join the 1AD Discord'),1)  # Single contextual onboarding; hero highlights analytics

    def test_owner_home_layout_and_links(self):
        p=Path(__file__).resolve().parents[1]/'docs'
        home=(p/'index.html').read_text()
        hero=home.split('<section class="hero motion-hero"',1)[1].split('</section>',1)[0]
        self.assertIn('Join the 1AD Discord',hero)
        self.assertEqual(home.count('Join the 1AD Discord'),1)
        self.assertNotIn('id="join-wardogs"',home)
        self.assertNotIn('id="ia-server-briefing"',home)
        self.assertIn('class="nav active" href="index.html"',home)
        self.assertIn('class="service-provenance"',home)
        for logo in ('1of1servers.com/brand/full-logo-white-amber.svg',
                     'assets/brands/warcon-logo-on-dark.svg',
                     'wardogstracker.gg/logo.png','logo_steam.svg'):
            self.assertIn(logo,home)
        self.assertTrue((p/'assets'/'brands'/'warcon-logo-on-dark.svg').is_file())
        self.assertIn('Only after you choose to connect and consent',home)
    def test_match_dialog_does_not_preserve_report_scroll(self):
        p=Path(__file__).resolve().parents[1]/'docs'
        script=(p/'js'/'app.js').read_text()
        self.assertNotIn('${location.pathname}#reports',script)
        self.assertIn('${location.pathname}${location.search}',script)
        for page in ('seasons.html','compare.html','weekly.html','players.html',
                     'activity.html','map-team.html','playerone-demo.html'):
            self.assertNotIn('href="index.html#reports"',(p/page).read_text())
