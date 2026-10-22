"""Discord Components V2 contract, result completeness and tie-safety regressions."""
import unittest
from src.discord_contract import faction_leaders
from src.discord_layout import match_recap


def played():
    return {
        "id": 401, "verifiedCompleted": True, "playerLinesComplete": True,
        "endedAt": "2026-10-22T18:40:00Z",
        "scores": [{"name":"Lonestar","score":100}],
        "winner": "Lonestar",
        "players": [
            {"key":"a","faction":"Lonestar","name":"Alpha","kills":21,"deaths":8},
            {"key":"b","faction":"Lonestar","name":"Bravo","kills":15,"deaths":6},
            {"key":"c","faction":"Valkyra","name":"Charlie","kills":17,"deaths":4},
            {"key":"d","faction":"Manticore","name":"Delta","kills":18,"deaths":5}
        ]
    }


class RecapV11ContractTests(unittest.TestCase):
    def test_faction_leaders_exactly_once_when_complete(self):
        data=played()
        leaders=faction_leaders(data)
        self.assertEqual([x["name"] for x in leaders],["Alpha","Charlie","Delta"])
        p=match_recap(data)
        self.assertEqual(p["flags"],32768)
        container=p["components"][0]
        self.assertEqual(container["accent_color"],0x465EFF)
        self.assertEqual(container["components"][1]["type"],12)
        self.assertEqual(container["components"][-1]["type"],1)
        button=container["components"][-1]["components"][0]
        self.assertEqual(button["style"],5)
        self.assertEqual(button["label"],"Open in 1ADAAR")
        self.assertEqual(button["url"],
                         "https://ejronin.github.io/1ADAAR/#match-401")
        self.assertNotIn("custom_id",button)
        self.assertNotIn("embeds",p)

    def test_incomplete_records_suppress_names(self):
        data=played()
        data["playerLinesComplete"]=False
        self.assertEqual(faction_leaders(data),[])
        p=match_recap(data)
        c=p["components"][0]["components"][2]["content"]
        self.assertIn("not shown",c)
        self.assertNotIn("Alpha",c)

    def test_ties_are_not_arbitrarily_assigned(self):
        data=played()
        data["players"].append(
            {"key":"e","faction":"Lonestar","name":"Echo","kills":21,"deaths":7})
        leaders=faction_leaders(data)
        self.assertTrue(leaders[0]["tie"])
        self.assertEqual(leaders[0]["tiedCount"],2)
        p=match_recap(data)
        self.assertIn("2 players tied",
                      p["components"][0]["components"][2]["content"])

    def test_duplicate_key_aggregates_and_unverified_suppresses(self):
        data=played()
        data["players"].append(
            {"key":"a","faction":"Lonestar","name":"Alpha","kills":3,"deaths":1})
        self.assertEqual(faction_leaders(data)[0]["kills"],24)
        data["verifiedCompleted"]=False
        self.assertEqual(faction_leaders(data),[])


if __name__=="__main__":
    unittest.main()
