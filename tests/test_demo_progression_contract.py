"""PlayerOne opt-in progression demo versus unlinked public dossier contract."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]/"docs"
class FictionalProgressionContractTests(unittest.TestCase):
    def test_only_demo_page_has_fictional_roles_and_simulated_connection(self):
        page=(ROOT/"playerone-demo.html").read_text()
        script=(ROOT/"js/demo-progression.js").read_text()
        radar=(ROOT/"js/role-radar.js").read_text()
        live=(ROOT/"players.html").read_text()
        assert 'data-fictional-demo="true"' in page
        assert page.index('id="demo-progression-panel"') < page.index('id="performance-module"')
        assert live.index('id="progression-panel"') < live.index('id="performance-module"')
        assert 'data-role-demo="true"' in page
        assert 'id="demo-role-radar"' in page
        assert 'id="demo-progression-connect"' in page
        assert 'id="demo-progression-refresh"' in page
        assert 'id="demo-progression-disconnect"' in page
        assert 'NOT CONNECTED · FICTIONAL PLAYER' in page
        assert 'not an official role-level maximum' in page
        assert 'demo-progression.js' in page
        assert 'FICTIONAL PLAYERONE FIXTURE' in script
        assert 'sourceStatus:\'fictional-demo\'' in script
        for role in ("Assault","Medic","Support","Recon","Driver","Pilot"):
            assert role in script
        assert "window.OneADAARRoleRadar.render" in script
        assert "document.body.dataset.fictionalDemo" in radar
        assert "svg.dataset.roleDemo" in radar
        assert "sourceStatus==='verified'" in radar
        assert "data-fictional-demo" not in live
        assert "demo-progression.js" not in live
        assert 'id="tracker-public-form"' in live\n        assert 'id="progression-check"' not in live
        assert 'id="progression-role-radar"' in live

    def test_navigation_exposes_player_map_and_activity_pages(self):
        for name in ("index.html","players.html","playerone-demo.html","weekly.html",
                     "activity.html","seasons.html","compare.html","map-team.html"):
            page=(ROOT/name).read_text()
            with self.subTest(name=name):
                assert 'href="players.html"' in page
                assert 'href="map-team.html"' in page
                assert 'href="activity.html"' in page

if __name__=="__main__":
    unittest.main()
