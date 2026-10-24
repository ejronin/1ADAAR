"""Match recap and next-round Discord posts are separate, source-verified and deduped."""
import datetime as dt
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from src.discord_layout import JOIN_CODE, match_recap, next_map_post
from src.next_round import confirmed_next_round
from src import recap

END = "2026-10-20T20:00:00Z"
OBS = "2026-10-20T20:02:00Z"
NOW = dt.datetime(2026,10,20,20,3,tzinfo=dt.timezone.utc)
MATCH = {"id": 402,"map":"Bakurani","endedAt":END,"winner":"Lonestar"}
STATUS = {"ok":True,"map":"Europe","lighting":"DayEarlyFog","observedAt":OBS}


class NextRoundTests(unittest.TestCase):
    def test_public_status_only_after_real_map_change_with_known_conditions(self):
        recorded=confirmed_next_round(STATUS,MATCH,now=NOW)
        self.assertEqual(recorded["map"],"Ozeti")
        self.assertEqual(recorded["conditions"],"Morning • Fog")
        self.assertIsNone(confirmed_next_round({**STATUS,"map":"Kavkazi"},MATCH,now=NOW))
        self.assertIsNone(confirmed_next_round({**STATUS,"lighting":None},MATCH,now=NOW))
        self.assertIsNone(confirmed_next_round({**STATUS,"ok":False},MATCH,now=NOW))
        self.assertIsNone(confirmed_next_round({**STATUS,"observedAt":"2026-10-20T19:50:00Z"},MATCH,now=NOW))
        self.assertIsNone(confirmed_next_round(STATUS,MATCH,now=NOW+dt.timedelta(hours=4)))
        self.assertIsNone(confirmed_next_round({**STATUS,"lighting":"TotallyUnknownWeather"},MATCH,now=NOW))

    def test_match_recap_has_no_next_map_guess_or_join_code(self):
        data=match_recap({**MATCH, 'verifiedCompleted':True})
        self.assertEqual(data["flags"],32768)
        self.assertEqual(data["components"][0]["components"][0]["content"],"## AFTER ACTION REPORT")
        self.assertIn("attachment://match-recap.png",json.dumps(data))
        self.assertIn("only if WARCON confirms",json.dumps(data))
        self.assertIn("See full report",json.dumps(data))
        self.assertNotIn(JOIN_CODE,json.dumps(data))
        self.assertNotIn("NEXT MAP:",json.dumps(data))
        self.assertNotIn("embeds",data)

    def test_follow_up_contains_verified_map_conditions_and_copyable_join_code(self):
        detail=confirmed_next_round(STATUS,MATCH,now=NOW)
        payload=next_map_post(MATCH,detail)
        self.assertEqual(payload["flags"],32768)
        content=json.dumps(payload,ensure_ascii=False)
        self.assertIn("NEXT MAP: Ozeti",content)
        self.assertIn("Morning • Fog",content)
        self.assertIn(JOIN_CODE,content)
        self.assertIn("SERVER JOIN CODE",content)
        self.assertIn("See more on 1ADAAR",content)
        self.assertEqual(payload["allowed_mentions"],{"parse":[]})
        with self.assertRaises(ValueError):
            next_map_post(MATCH,{"map":"Ozeti","conditions":"Sunny","source":"guessed"})

    def test_second_post_is_idempotent_and_not_posted_before_confirmation(self):
        from src.recap import DATA
        with tempfile.TemporaryDirectory() as d:
            dest=Path(d)
            # Pretend a completed real report was already delivered.
            (dest/"delivery.json").write_text(json.dumps({"initialized":True,"posted":{"402":"89765"}}))
            (dest/"matches.json").write_text(json.dumps({"matches":[]}))
            raw={"id":402,"startedAt":"2026-10-20T19:40:00Z","endedAt":END,
                 "map":"Kavkazi","experiences":"Bakurani_KOTH_01","finalScores":[{"name":"Lonestar","score":100}],
                 "winner":"Lonestar"}
            detail={"ok":True,"match":raw,"lines":[],"awards":[],"hasFeed":False}
            responses={"state":None}
            def lookup(url):
                if "?page=" in url:
                    return {"ok":True,"matches":[raw],"pages":1}
                if url.endswith("/402"):
                    return detail
                if url == recap.PUBLIC_STATUS:
                    return {"ok":True,"server":responses["state"] or {}}
                return {"ok":True,"players":[],"page":1,"pages":1}
            with patch.object(recap,'DATA',dest),patch.object(recap,'fetch_json',side_effect=lookup),patch.object(recap,'send_discord',return_value="2999") as sender,patch('src.next_round.confirmed_next_round',side_effect=lambda status,match: confirmed_next_round(status,match,now=NOW)):
                recap.run(webhook="https://discord.com/api/webhooks/123456/validtoken")
                sender.assert_not_called()
                responses["state"]=STATUS
                recap.run(webhook="https://discord.com/api/webhooks/123456/validtoken")
                self.assertEqual(sender.call_count,1)
                payload=sender.call_args.args[1]
                self.assertIn("NEXT MAP: Ozeti",json.dumps(payload))
                recap.run(webhook="https://discord.com/api/webhooks/123456/validtoken")
                self.assertEqual(sender.call_count,1)
                checkpoint=json.loads((dest/"next-round-delivery.json").read_text())
                self.assertEqual(checkpoint["posted"]["402"],"2999")


if __name__=="__main__":
    unittest.main()
