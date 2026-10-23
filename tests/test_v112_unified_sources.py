"""Release gates for unified 1ADAAR layout, trustworthy data sources and map imagery."""
from pathlib import Path
from html.parser import HTMLParser
import unittest

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/'docs'
PAGES=('index.html','seasons.html','players.html','map-team.html',
       'activity.html','progression.html','compare.html','weekly.html')
NAV=('index.html','seasons.html','players.html','map-team.html',
     'activity.html','progression.html','compare.html','weekly.html')

class Inspector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.styles=[]
        self.nav=[]
        self.images=[]
        self.scripts=[]
    def handle_starttag(self,tag,attrs):
        data=dict(attrs)
        if tag=='link' and data.get('rel')=='stylesheet':
            self.styles.append(data.get('href'))
        if tag=='a' and 'nav' in (data.get('class') or '').split():
            self.nav.append(data.get('href'))
        if tag=='img':
            self.images.append(data.get('src'))
        if tag=='script' and data.get('src'):
            self.scripts.append(data.get('src'))

class UnifiedSiteTests(unittest.TestCase):
    def test_every_active_page_has_same_nav_and_game_brand(self):
        for page in PAGES:
            html=(DOCS/page).read_text()
            parser=Inspector()
            parser.feed(html)
            with self.subTest(page=page):
                self.assertEqual(parser.nav[:8],list(NAV))
                self.assertEqual(parser.nav.count(page),1)
                self.assertIn('assets/wardogs-fullmark.png',parser.images)
                self.assertEqual(parser.styles[-1], 'assets/server-map-feature.css?v=118' if page=='index.html' else ('assets/map-gallery.css?v=117' if page=='map-team.html' else 'assets/site-unified.css?v=112'))
                self.assertEqual(sum('site-unified.css' in x for x in parser.styles),1)
                self.assertEqual(html.count('1of1 Servers'),1)
                self.assertEqual(html.count('alt="WARCON"'),1)
                self.assertEqual(html.count('alt="WARDOGS Tracker"'),1)
                self.assertEqual(html.count('alt="Steam"'),1)
                self.assertIn('href="https://1of1servers.com/"',html)
                self.assertNotIn('game artwork',html.lower())
                for url in parser.styles+parser.scripts:
                    self.assertTrue((DOCS/url.split('?')[0]).is_file(),url)

    def test_source_is_not_misrepresented_as_global_combat(self):
        js=(DOCS/'js/player-snapshot.js').read_text()
        self.assertIn("'1AD SERVER'",js)
        self.assertIn("'TRACKER · ALL'",js)
        self.assertIn("'—'",js)
        self.assertIn('Tracker does not publish global combat totals',js)
        self.assertNotIn('globalKd',js)
        self.assertIn('career-source-pair',(DOCS/'assets/site-unified.css').read_text())
        self.assertIn('js/player-snapshot.js?v=112',(DOCS/'players.html').read_text())

    def test_map_label_cards_are_real_reproducible_assets(self):
        script=(ROOT/'scripts/build_map_banners.py').read_text()
        decorator=(DOCS/'js/map-banners.js').read_text()
        style=(DOCS/'assets/site-unified.css').read_text()
        collector=(ROOT/'.github/workflows/collect.yml').read_text()
        for name in ('bakurani','ozeti','zestafona'):
            self.assertTrue((DOCS/'assets/map-banners'/f'{name}.webp').is_file())
            self.assertIn(name,script)
            self.assertIn(name,decorator)
        self.assertIn('-card.webp',decorator)
        self.assertIn('map-banner-named',style)
        self.assertIn('scripts/build_map_banners.py',collector)
        self.assertIn('git add docs/assets/map-banners/*-card.webp',collector)
        self.assertIn('js/map-banners.js?v=117',(DOCS/'index.html').read_text())

    def test_no_competing_source_navigation_or_duplicated_hero_baselines(self):
        unified=(DOCS/'assets/site-unified.css').read_text()
        for fragment in ('--site-max:1520px','--site-hero-height:430px',
                         '.weekly-hero,.mt-hero,.act-hero,.season-hero,.compare-hero,.ia-titlebar',
                         '.rail-footer.rail-sources{display:grid',
                         '.weekly-page .weekly-hero','--weekly-blue:#83b8e9',
                         '.weekly-page .weekly-podium-place.gold'):
            # The metallic podium is supplied by weekly.css, intentionally outside the shared theme.
            if fragment=='.weekly-page .weekly-podium-place.gold':
                self.assertIn(fragment,(DOCS/'assets/weekly.css').read_text())
            else:self.assertIn(fragment,unified)
        self.assertIn('v=112',(DOCS/'weekly.html').read_text())
        self.assertIn('v=112',(DOCS/'index.html').read_text())

if __name__=='__main__':
    unittest.main()
