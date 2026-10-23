"""Owner-approved hero wording and truthful map-image opt-in contract."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class HeroCopyContract(unittest.TestCase):
    def test_exact_owner_selected_hero_wording(self):
        expected={
            "index.html":("MATCHES. PLAYERS.","RESULTS.","Track completed matches"),
            "players.html":("PLAYER ","DOSSIER.","Review saved match results"),
            "activity.html":("WHEN THE SERVER ","GETS HOT.","Recorded completed-match starts"),
            "weekly.html":("THIS WEEK ","ON THE SERVER.","Top performers, archived results"),
            "map-team.html":("MAPS. FACTIONS. ","OUTCOMES.","See where you perform best"),
            "compare.html":("HEAD ","TO HEAD.","Compare two players side by side"),
            "seasons.html":("ARCHIVED ","MATCHES.","Browse older saved reports"),
            "playerone-demo.html":("PLAYERONE ","SAMPLE.","A fictional player dossier"),
        }
        for page,fragments in expected.items():
            s=(ROOT/'docs'/page).read_text(encoding='utf-8')
            with self.subTest(page=page):
                for phrase in fragments:self.assertIn(phrase,s)
        compare=(ROOT/'docs/compare.html').read_text()
        self.assertIn('Saved-match trends are not part of this comparison.',compare)

    def test_vertical_emblem_and_map_artwork_fallback_are_explicit(self):
        css=(ROOT/'docs/assets/ia-v11.css').read_text()
        self.assertIn('.player-hero .player-hero-logo{',css)
        self.assertIn('transform:translateY(-50%)',css)
        recap=(ROOT/'src/recap_card.py').read_text()
        self.assertIn('banner_for_map(match.get("map")) or ART',recap)
        map_js=(ROOT/'docs/js/map-team.js').read_text()
        self.assertIn('decorateMapRow(card,record.name)',map_js)
        manifest=(ROOT/'docs/assets/map-banners/manifest.json').read_text()
        self.assertIn('"images": {}',manifest)


if __name__=='__main__':
    unittest.main()
