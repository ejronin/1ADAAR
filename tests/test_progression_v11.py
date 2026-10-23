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

    def test_public_profile_requires_explicit_browser_opt_in(self):
        live=(ROOT/"docs/players.html").read_text()
        standalone=(ROOT/"docs/progression.html").read_text()
        js=(ROOT/"docs/js/progression.js").read_text()
        config=(ROOT/"docs/js/progression-config.js").read_text()
        for page in (live,standalone):
            self.assertIn('id="tracker-public-form"',page)
            self.assertIn('src="js/progression.js?v=4"',page)
            self.assertIn('id="tracker-public-id"',page)
            self.assertIn('id="tracker-public-remember"',page)
            self.assertIn('id="tracker-public-economy"',page)
            self.assertIn('id="tracker-community-form"',page)
            self.assertIn('1ADAAR is not affiliated with Steam',page)
            self.assertNotIn('id="progression-check"',page)
        self.assertIn("https://wardogstracker.gg/profile/",js)
        self.assertIn("root.OneADAARRoleRadar",js)
        self.assertIn("1ADAAR:v1:",js)
        self.assertIn("getSaved()",js)
        self.assertIn("credentials:'omit'",js)
        self.assertIn("sourceStatus:'verified'",js)
        self.assertNotIn("/auth/start",js)
        self.assertNotIn("workers.dev",config)
        self.assertIn("endpoint:''",config)


if __name__=="__main__":
    unittest.main()
