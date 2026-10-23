"""Owner approval gates for the live player dossier and non-fictional release."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'

class OwnerLiveReleaseTests(unittest.TestCase):
    def test_demo_is_no_longer_public_and_dossier_is_complete(self):
        self.assertFalse((DOCS/'playerone-demo.html').exists())
        self.assertFalse((DOCS/'data/demo-player.json').exists())
        self.assertTrue((ROOT/'tests/fixtures/playerone-demo.html').exists())
        page=(DOCS/'players.html').read_text()
        self.assertNotIn('href="playerone-demo.html"',page)
        for marker in ('id="profile-metrics"','id="profile-secondary"',
                       'id="performance-module"','id="player-snapshot"',
                       'id="combat-metrics"','id="progression-panel"',
                       'id="map-breakdown"','id="faction-breakdown"',
                       'id="recent-match-table"','id="map-team-details"'):
            self.assertIn(marker,page)
        js=(DOCS/'js/players.js').read_text()
        self.assertIn("OneADAARProfile.career",js)
        self.assertIn("OneADAARPerformance.mount",js)
        self.assertIn("OneADAARProfile.snapshot",js)
        self.assertIn("OneADAARProgression.mount",js)
        self.assertIn("1adaar-selected-player-key-v1",js)

    def test_map_team_has_real_in_page_selection_and_no_fake_results(self):
        page=(DOCS/'map-team.html').read_text()
        js=(DOCS/'js/map-team.js').read_text()
        for marker in ('id="mt-player-search"','id="mt-player-query"',
                       'id="mt-player-results"','id="mt-career-grid"',
                       'id="mt-maps"','id="mt-factions"','id="mt-combinations"'):
            self.assertIn(marker,page)
        self.assertIn("data/players.json",js)
        self.assertIn("1adaar-selected-player-key-v1",js)
        self.assertIn("showCareer(selected)",js)
        self.assertIn("decorateMapRow(card,record.name)",js)
        self.assertNotIn("demo-playerone",page+js)

    def test_radars_scale_to_actual_highest_level_not_hardcoded_100(self):
        js=(DOCS/'js/role-radar.js').read_text()
        self.assertIn("scaleFor(record.levels)",js)
        self.assertIn("record.levels[name]/displayMax",js)
        self.assertIn("ALL VERIFIED ROLES AT LEVEL 0",js)
        for page in ('players.html','progression.html'):
            self.assertIn('id="progression-radar-scale"',(DOCS/page).read_text())

    def test_source_logos_across_live_pages(self):
        for page in ('index.html','players.html','weekly.html','map-team.html',
                     'progression.html','activity.html','seasons.html','compare.html'):
            html=(DOCS/page).read_text()
            for marker in ('1of1servers.com/brand/full-logo-white-amber.svg',
                           'assets/brands/warcon-logo-on-dark.svg',
                           'assets/wardogs-fullmark.png','wardogstracker.gg/logo.png',
                           'logo_steam.svg','OPTIONAL PROFILE IMAGE*'):
                self.assertIn(marker,html,(page,marker))
        self.assertNotIn('data-steam-logo',(DOCS/'index.html').read_text())

    def test_weekly_podium_is_ranked_with_decorative_crown(self):
        html=(DOCS/'weekly.html').read_text()
        css=(DOCS/'assets/weekly.css').read_text()
        self.assertIn('class="weekly-crown" aria-hidden="true"',html)
        self.assertIn('data-award-verified="false"',html)
        for marker in ('min-height:296px','min-height:260px','min-height:221px',
                       'weekly-crown-arrive','prefers-reduced-motion'):
            self.assertIn(marker,css)

    def test_no_digital_anarchy_lookup_and_honest_kill_feed_caveat(self):
        for page in ('players.html','progression.html'):
            html=(DOCS/page).read_text()
            self.assertNotIn('tracker-community-form',html)
            self.assertNotIn('ce8ecb97',html)
            self.assertIn('Some community servers do not enable or publish kill-feed reporting',html)
        js=(DOCS/'js/progression.js').read_text()
        self.assertNotIn('tracker-community-server',js)
        self.assertNotIn('/api/v1/servers/',js)

if __name__=='__main__':
    unittest.main()
