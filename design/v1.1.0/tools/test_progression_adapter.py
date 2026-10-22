import importlib.util
import json
from pathlib import Path
import unittest

PATH=Path(__file__).resolve().parents[1]/"components"/"progression_adapter.py"
spec=importlib.util.spec_from_file_location("progression_adapter",PATH)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
SID="76561198000000000"
def fixture():
    return {"player":{"steamId":SID,"stats":{"roles":{
       role.lower():{"level":i+11,"xp":(i+1)*1000} for i,role in enumerate(mod.ROLES)
    },"syncedAt":"2026-10-21T13:00:00.000Z"}},"source":"WARDOGS Tracker"}

class ProgressionAdapterTests(unittest.TestCase):
    def test_exact_six_axes_no_ids_in_public_result(self):
        got=mod.normalize_tracker_progression(fixture(),requested_steam_id=SID,
            public_display_approved=True,max_level=100)
        self.assertEqual(set(got["levels"]),set(mod.ROLES))
        self.assertEqual(got["levels"]["Assault"],11)
        self.assertEqual(got["xp"]["Pilot"],6000)
        self.assertIn("wardogstracker.gg/developers",got["sourceUrl"])
        self.assertNotIn(SID,json.dumps(got))
        self.assertNotIn("steamId",json.dumps(got))
    def test_gates_required(self):
        for condition in (
          dict(public_display_approved=False,max_level=100),
          dict(public_display_approved=True,max_level=None),
          dict(public_display_approved=True,max_level=0),
        ):
            with self.subTest(**condition):
                self.assertIsNone(mod.normalize_tracker_progression(fixture(),requested_steam_id=SID,**condition))
    def test_privacy_and_wrong_identity_fail_closed(self):
        for bad in ({"player":{"steamId":SID,"stats":None}},
                    {"player":{"steamId":"76561198000000099","stats":fixture()["player"]["stats"]}},
                    {"error":"Not found"}):
            self.assertIsNone(mod.normalize_tracker_progression(bad,requested_steam_id=SID,
                public_display_approved=True,max_level=100))
    def test_incomplete_nonfinite_and_stale_source_fail(self):
        src=fixture();del src["player"]["stats"]["roles"]["pilot"]
        self.assertIsNone(mod.normalize_tracker_progression(src,requested_steam_id=SID,public_display_approved=True,max_level=100))
        src=fixture();src["player"]["stats"]["roles"]["pilot"]["level"]=float("nan")
        self.assertIsNone(mod.normalize_tracker_progression(src,requested_steam_id=SID,public_display_approved=True,max_level=100))
        src=fixture();src["player"]["stats"]["syncedAt"]="unverified"
        self.assertIsNone(mod.normalize_tracker_progression(src,requested_steam_id=SID,public_display_approved=True,max_level=100))

if __name__=="__main__":unittest.main()
