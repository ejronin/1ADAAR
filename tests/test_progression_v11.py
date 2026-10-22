"""Source-gated v1.1 progression tests; no network, Steam sessions, or raw IDs in Pages."""
from __future__ import annotations
import unittest
from pathlib import Path
from src.progression_adapter import normalize_tracker_progression

SID = "76561190000000001"
ROLES = ("assault", "medic", "support", "recon", "driver", "pilot")
ROOT = Path(__file__).resolve().parents[1]


def payload(*, economy=True):
    return {"player": {
        "steamId": SID,
        "stats": {
            "wardogLevel": 19, "careerXp": 50001,
            "cash": 0 if economy else None, "gold": None,
            "syncedAt": "2026-10-21T18:00:00Z",
            "roles": {name: {"level": idx+1, "xp": (idx+1)*100}
                      for idx, name in enumerate(ROLES)}
        }
    }}


class TrackerDataPrivacyTests(unittest.TestCase):
    def test_explicit_approval_and_ownership_link_are_mandatory(self):
        self.assertIsNone(normalize_tracker_progression(
            payload(), requested_steam_id=SID, public_display_approved=False, max_level=100))
        self.assertIsNone(normalize_tracker_progression(
            payload(), requested_steam_id="76561190000000002",
            public_display_approved=True, max_level=100))
        self.assertIsNone(normalize_tracker_progression(
            payload(), requested_steam_id=SID, public_display_approved=True,
            max_level=None))

    def test_complete_six_roles_and_nullable_economy(self):
        result=normalize_tracker_progression(
            payload(), requested_steam_id=SID, public_display_approved=True,
            max_level=100)
        self.assertIsNotNone(result)
        self.assertEqual(result["wardogLevel"],19)
        self.assertEqual(result["careerXp"],50001)
        self.assertEqual(len(result["levels"]),6)
        self.assertEqual(result["xp"]["Pilot"],600)
        self.assertEqual(result["cash"],0)
        self.assertIsNone(result["gold"])
        self.assertEqual(result["economyStatus"]["gold"],"hidden_or_unavailable")
        self.assertNotIn("steamId",result)
        self.assertNotIn(SID,str(result))
        result2=normalize_tracker_progression(
            payload(economy=False),requested_steam_id=SID,
            public_display_approved=True,max_level=100)
        self.assertIsNone(result2["cash"])

    def test_incomplete_stats_are_never_renderable(self):
        incomplete=payload()
        del incomplete["player"]["stats"]["roles"]["medic"]
        self.assertIsNone(normalize_tracker_progression(
            incomplete,requested_steam_id=SID,public_display_approved=True,max_level=100))
        incomplete=payload()
        incomplete["player"]["stats"]["roles"]["pilot"]["xp"]=-4
        self.assertIsNone(normalize_tracker_progression(
            incomplete,requested_steam_id=SID,public_display_approved=True,max_level=100))

    def test_static_pages_cannot_claim_authentication(self):
        js=(ROOT/"docs/js/progression.js").read_text()
        html=(ROOT/"docs/players.html").read_text()
        self.assertIn("wardogstracker.gg/stats",html)
        self.assertIn("Steam ownership",js)
        self.assertNotIn(SID,(ROOT/"docs/js/progression.js").read_text())
        self.assertIn("No verified progression connection",html)
        self.assertTrue((ROOT/"docs/js/role-radar.js").is_file())
        self.assertIn('id="progression-role-radar"',html)
        self.assertIn('data-role-empty="true"',html)
        self.assertIn('root.OneADAARRoleRadar.render',js)


if __name__=="__main__":
    unittest.main()
