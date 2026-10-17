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
        self.assertEqual(s.count('Join the 1AD Discord'),2)  # Hero + context-specific onboarding
