"""Design-source parity with the committed original fictional PlayerOne fixture."""
from collections import Counter
from datetime import datetime
from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"design"/"v1.1.0"/"prototypes"
FIXTURE=ROOT/"docs"/"data"/"demo-player.json"

class FixtureParityTest(unittest.TestCase):
    def setUp(self):
        self.f=json.loads(FIXTURE.read_text())
        self.assertTrue(self.f["fictional"])
        self.assertEqual(self.f["kind"],"demo-only")
        self.latest=sorted(self.f["matches"],key=lambda m:m["endedAt"],reverse=True)[:10]
        self.player=(BASE/"player.html").read_text()
        self.map=(BASE/"map-team.html").read_text()

    def test_original_career_values_unchanged(self):
        p=self.f["player"]
        for number in ("634","332","48","27","37h","3h","1.91"):
            self.assertIn(number,self.player)
        self.assertEqual((p["wins"],p["losses"],p["draws"]),(27,17,4))
        self.assertEqual(len(self.f["matches"]),32)
        for label in ("Headshots","Vehicle kills","Best kill streak","Team kills"):
            self.assertIn(label,self.player)

    def test_original_last_ten_match_rows_match_player_table(self):
        for m in self.latest:
            p=m["players"][0]
            date=datetime.fromisoformat(m["endedAt"].replace("Z","+00:00"))
            label=date.strftime("%b ") + str(date.day)
            row=f"<tr><td>{label}</td><td>{m['map']}</td><td>{p['faction']}</td>"
            with self.subTest(date=label,map=m["map"]):
                self.assertIn(row,self.player)
                self.assertIn(f"<td>{p['kills']}</td><td>{p['deaths']}</td></tr>",self.player)

    def test_map_fixture_outcomes_and_kd_are_derived_not_improvised(self):
        outcomes=Counter(m["players"][0]["result"] for m in self.latest)
        self.assertEqual(outcomes,{"win":5,"loss":4,"draw":1})
        for text in ('>5</strong><div class="sub">Wins',
                     '>4</strong><div class="sub">Losses',
                     '>1</strong><div class="sub">Draws'):
            self.assertIn(text,self.map)
        for mapname in ("Bakurani","Ozeti","Zestafona"):
            rows=[m for m in self.latest if m["map"]==mapname]
            kills=sum(m["players"][0]["kills"] for m in rows)
            deaths=sum(m["players"][0]["deaths"] for m in rows)
            kd=round(kills/deaths,2)
            with self.subTest(map=mapname):
                self.assertIn(f"{kd:.2f} · {len(rows)} matches",self.player)
                self.assertIn(f"{kd:.2f} · {len(rows)} matches",self.map)

    def test_faction_map_cross_tab_follows_observed_rows(self):
        html=self.map
        for mapname,team in (("Bakurani","Lonestar"),("Ozeti","Valkyra"),("Zestafona","Manticore")):
            subset=[m for m in self.latest if m["map"]==mapname]
            self.assertTrue(all(m["players"][0]["faction"]==team for m in subset))
            self.assertIn(f"{len(subset)} recorded",html)
        self.assertIn("unobserved",html)

    def test_live_source_gates_not_replaced_by_pretend_data(self):
        activity=(BASE/"activity.html").read_text()
        self.assertIn("NO VERIFIED ROLE LEVELS",activity)
        self.assertIn("WARDOGS Tracker",activity)
        self.assertIn("ZERO CAPTURED MATCHES",activity)
        self.assertIn("role_radar.js",activity)
        js=(BASE/"shared.js").read_text()
        self.assertIn("fetch('../../../docs/data/demo-player.json'",js)
        self.assertIn("tabs=$$('.tab[data-trend]')",js)
        self.assertIn("pairedCounts(",js)

if __name__=="__main__":
    unittest.main()
