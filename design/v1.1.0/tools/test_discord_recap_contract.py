import importlib.util
from pathlib import Path
import json
import unittest

FILE=Path(__file__).resolve().parents[1]/"components"/"discord_recap_contract.py"
spec=importlib.util.spec_from_file_location("recap_contract",FILE)
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def match(complete=True):
    return {"id":12,"verifiedCompleted":True,"playerLinesComplete":complete,
            "players":[
                {"key":"u1","faction":"Lonestar","name":"OperatorA","kills":19,"deaths":4},
                {"key":"u2","faction":"Lonestar","name":"OperatorB","kills":11,"deaths":5},
                {"key":"u3","faction":"Valkyra","name":"MedicB","kills":8,"deaths":4},
                {"key":"u4","faction":"Manticore","name":"MarksmanC","kills":14,"deaths":6}
            ]}

class RecapContractTest(unittest.TestCase):
    def test_real_link_button_and_discord_v2_fields(self):
        p=m.build_design_recap(match())
        self.assertEqual(p["flags"],32768)
        self.assertNotIn("content",p)
        self.assertNotIn("embeds",p)
        self.assertEqual(p["allowed_mentions"],{"parse":[]})
        container=p["components"][0]
        self.assertEqual(container["type"],17)
        self.assertEqual(container["components"][1]["type"],12)
        self.assertEqual(container["components"][1]["items"][0]["media"]["url"],"attachment://match-recap.png")
        button=container["components"][-1]["components"][0]
        self.assertEqual(button,{"type":2,"style":5,"label":"Open in 1ADAAR","url":"https://ejronin.github.io/1ADAAR/"})
        self.assertNotIn("custom_id",button)
    def test_top_one_per_faction_requires_full_lines(self):
        data=m.faction_leaders(match())
        self.assertEqual([x["faction"] for x in data],list(m.FACTIONS))
        self.assertEqual(data[0]["name"],"OperatorA")
        self.assertEqual(data[1]["name"],"MedicB")
        self.assertEqual(data[2]["kills"],14)
        missing=m.build_design_recap(match(False))["components"][0]["components"][2]["content"]
        self.assertIn("not shown",missing)
        self.assertNotIn("OperatorA",missing)
    def test_ties_not_arbitrarily_awarded(self):
        source=match()
        source["players"].append({"key":"u5","faction":"Lonestar","name":"OperatorZ","kills":19,"deaths":7})
        a=m.faction_leaders(source)
        self.assertTrue(a[0]["tie"])
        self.assertIsNone(a[0]["name"])
    def test_invalid_payload_and_non_firstparty_links_rejected(self):
        data=match();data["verifiedCompleted"]=False
        with self.assertRaises(ValueError):m.build_design_recap(data)
        with self.assertRaises(ValueError):m.build_design_recap(match(),dashboard_url="https://attacker.example/report")
    def test_absent_session_ids_public(self):
        p=m.build_design_recap(match())
        text=json.dumps(p)
        self.assertNotIn("steamId",text)

if __name__=="__main__":unittest.main()
