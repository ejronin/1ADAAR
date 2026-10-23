import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]/'docs'

class OfficialFactionArtworkTests(unittest.TestCase):
    def test_source_traced_emblems_have_correct_color_identity(self):
        expected={'lonestar':'#3952e8','valkyra':'#e13329','manticore':'#3da832'}
        for name,color in expected.items():
            file=ROOT/'assets'/'factions'/f'{name}.svg'
            self.assertTrue(file.is_file())
            root=ET.parse(file).getroot()
            self.assertTrue(root.tag.endswith('svg'))
            self.assertIn(color, file.read_text())
            self.assertIn('viewBox="0 0 256 256"',file.read_text())
    def test_only_real_factions_are_mapped(self):
        js=(ROOT/'js'/'factions.js').read_text()
        for name in ('lonestar','valkyra','manticore'):
            self.assertIn(name,js)
            self.assertIn('assets/factions/'+name+'.svg',js)
        self.assertIn("palette[name.trim().toLowerCase()]||null",js)
        self.assertIn("text.textContent=String(name||'—')",js)
    def test_real_and_demo_pages_include_markers_and_colors(self):
        for page in ('index.html','players.html'):
            html=(ROOT/page).read_text()
            self.assertIn('assets/factions.css?v=1',html)
            self.assertIn('src="js/factions.js?v=1"',html)
        demo=((Path(__file__).resolve().parents[1]/'tests/fixtures/playerone-demo.html')).read_text()
        self.assertIn('class="profile-panel faction-breakdown"',demo)
        for name in ('lonestar','valkyra','manticore'):
            self.assertIn(f'src="assets/factions/{name}.svg"',demo)
        player=(ROOT/'js/players.js').read_text()
        app=(ROOT/'js/app.js').read_text()
        self.assertIn('OneADAARFactions.label',player)
        self.assertIn('OneADAARFactions.label',app)
        self.assertIn('OneADAARFactions.identify(s.name)',app)
    def test_mobile_and_contrast(self):
        css=(ROOT/'assets/factions.css').read_text()
        self.assertIn('@media(max-width:720px)',css)
        self.assertIn('faction-lonestar',css)
        self.assertIn('faction-valkyra',css)
        self.assertIn('faction-manticore',css)
        self.assertIn('--faction-accent',css)
