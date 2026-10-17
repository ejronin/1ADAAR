import datetime as dt
import unittest
from src.server_status import project, unknown

NOW=dt.datetime(2026,10,16,22,0,tzinfo=dt.timezone.utc)
BASE={"ok":True,"observedAt":"2026-10-16T21:59:00Z",
      "players":27,"maxPlayers":100,"map":"NorthAmerica",
      "roster":[{"steamId":"76561190000000001"}],
      "joinCode":"SERVER JOIN PRIVATE TO 1ADAAR",
      "scores":[{"name":"Lonestar","score":100}]}

class PublicServerStatusTests(unittest.TestCase):
    def test_online_player_count_map_and_private_fields(self):
        result=project(BASE,"offline",now=NOW)
        self.assertEqual(result["state"],"online")
        self.assertEqual(result["players"],27)
        self.assertEqual(result["maxPlayers"],100)
        self.assertEqual(result["map"],"Zestafona")
        self.assertNotIn("joinCode",result)
        self.assertNotIn("roster",result)
        self.assertNotIn("steamId",str(result))
    def test_zero_players_is_live_not_offline(self):
        v=project({**BASE,"players":0},"unknown",now=NOW)
        self.assertEqual(v["state"],"online")
        self.assertEqual(v["players"],0)
    def test_online_to_offline_transition_is_reconnecting_then_offline(self):
        offline={**BASE,"ok":False,"players":0}
        first=project(offline,"online",now=NOW)
        self.assertEqual(first["state"],"reconnecting")
        self.assertIsNone(first["players"])
        self.assertIsNone(first["map"])
        self.assertEqual(project(offline,first["state"],now=NOW)["state"],"offline")
        self.assertEqual(project(offline,"unknown",now=NOW)["state"],"offline")
    def test_stale_observation_or_invalid_status_cannot_be_live_or_offline(self):
        old={**BASE,"observedAt":"2026-10-16T21:30:00Z"}
        self.assertEqual(project(old,"online",now=NOW)["state"],"unknown")
        self.assertEqual(project({**BASE,"observedAt":None},"online",now=NOW)["state"],"unknown")
        self.assertEqual(project({**BASE,"ok":"true"},"online",now=NOW)["state"],"unknown")
        self.assertEqual(project({**BASE,"observedAt":"2026-10-16T22:10:00Z"},"online",now=NOW)["state"],"unknown")
    def test_unsupported_maps_do_not_claim_team_state(self):
        self.assertEqual(project({**BASE,"map":"Community_NewMap"},"online",now=NOW)["map"],"Community_NewMap")
        self.assertIsNone(project({**BASE,"map":None},"online",now=NOW)["map"])
        self.assertEqual(unknown(NOW)["state"],"unknown")
    def test_invalid_counters_never_become_live_counts(self):
        self.assertIsNone(project({**BASE,"players":True},"online",now=NOW)["players"])
        self.assertIsNone(project({**BASE,"players":-1},"online",now=NOW)["players"])
