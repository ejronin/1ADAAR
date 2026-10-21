import unittest
from unittest.mock import patch
from pathlib import Path
import tempfile
import json
from src import recap

SAMPLE = {
    "id": 812, "startedAt": "2026-10-15T21:00:00Z", "endedAt": "2026-10-15T21:47:00Z",
    "map": "Kavkazi", "experiences": "Bakurani_KOTH_01", "lighting": "DayLateRain",
    "peakPlayers": 73, "players": 67,
    "finalScores": [{"name":"Lonestar","score":100},{"name":"Valkyra","score": 82},{"name":"Manticore","score":64}],
    "winner":"Lonestar"
}
DETAIL = {"ok": True,"match":SAMPLE,"awards":[{"key":"kills","label":"Most kills","steamId":"76561190000000001","name":"Ace","value":"33"}],
          "lines":[{"steamId":"76561190000000001","name":"Ace","faction":"Lonestar","kills":33,"deaths":8,"seconds":2100}],"hasFeed": True}

class TestCollector(unittest.TestCase):
    def test_public_payload_strips_ids_and_limits_fields(self):
        result = recap.public_match(SAMPLE, DETAIL)
        text = json.dumps(result)
        self.assertEqual(result['durationSeconds'], 2820)
        self.assertEqual(result['map'], 'Bakurani')
        self.assertEqual(result['mode'], 'King of the Hill')
        self.assertNotIn('steamId', text)
        self.assertNotIn('76561190000000001', text)
        self.assertEqual(result['scores'][0]['score'], 100)
    def test_abandoned_and_running_not_posted(self):
        self.assertFalse(recap.usable_match({**SAMPLE,'endedAt':None}))
        self.assertFalse(recap.usable_match({**SAMPLE,'finalScores':None}))
    def test_malicious_names_cannot_ping_everyone(self):
        sample={**SAMPLE,'winner':'@everyone','finalScores':[{'name':'@here', 'score':100}]}
        p=recap.discord_payload(recap.public_match(sample,DETAIL))
        self.assertEqual(p['allowed_mentions'], {'parse':[]})
        self.assertNotIn('@everyone',json.dumps(p))
    def test_first_run_baselines_no_old_matches_posted(self):
        with tempfile.TemporaryDirectory() as temp:
            def response(url):
                return {'ok':True,'matches':[SAMPLE],'pages':1} if '?page=' in url else DETAIL
            with patch.object(recap,'DATA',Path(temp)),patch.object(recap,'fetch_json',side_effect=response),patch.object(recap,'send_discord') as sender:
                summary=recap.run(webhook='https://discord.com/api/webhooks/12345/longtoken')
                self.assertEqual(summary['matches'],1)
                self.assertEqual(sender.call_count,0)
                ledger=json.loads((Path(temp)/'delivery.json').read_text())
                self.assertEqual(ledger['posted']['812'],'baseline')
    def test_new_match_posts_only_once(self):
        with tempfile.TemporaryDirectory() as temp:
            newer={**SAMPLE,'id':813,'endedAt':'2026-10-15T22:47:00Z'}
            state={'new':False}
            def response(url):
                if '?page=' in url:
                    return {'ok':True,'matches':[newer,SAMPLE] if state['new'] else [SAMPLE],'pages':1}
                return {**DETAIL,'match':newer if url.endswith('813') else SAMPLE}
            with patch.object(recap,'DATA',Path(temp)),patch.object(recap,'fetch_json',side_effect=response),patch.object(recap,'send_discord',return_value='111111') as sender:
                recap.run(webhook='https://discord.com/api/webhooks/12345/longtoken')
                state['new']=True
                recap.run(webhook='https://discord.com/api/webhooks/12345/longtoken')
                recap.run(webhook='https://discord.com/api/webhooks/12345/longtoken')
                self.assertEqual(sender.call_count,1)
    def test_discord_primary_link_opens_github_report_for_completed_match(self):
        m=recap.public_match(SAMPLE,DETAIL)
        payload=recap.discord_payload(m)
        self.assertEqual(payload['flags'],32768)
        self.assertNotIn('embeds',payload)
        self.assertNotIn('content',payload)
        layout=payload['components'][0]
        self.assertEqual(layout['type'],17)
        self.assertEqual(layout['components'][0]['content'],'## AFTER ACTION REPORT')
        self.assertEqual(layout['components'][1]['type'],12)
        self.assertIn('attachment://match-recap.png',json.dumps(layout))
        self.assertIn("only if WARCON confirms",json.dumps(layout))
        self.assertEqual(payload['components'][1]['components'][0]['url'],
                         f"{recap.SITE_URL}#match-812")
        self.assertEqual(payload['allowed_mentions'],{'parse':[]})
    def test_match_must_end_with_final_scores_before_posting(self):
        self.assertFalse(recap.usable_match({**SAMPLE, 'endedAt':None}))
        self.assertFalse(recap.usable_match({**SAMPLE, 'finalScores':None}))
        self.assertFalse(recap.usable_match({**SAMPLE, 'finalScores':[]}))
        self.assertFalse(recap.usable_match({**SAMPLE, 'endedAt':'2026-10-15T20:00:00Z'}))
        self.assertTrue(recap.usable_match(SAMPLE))
    def test_site_url_is_correct(self):
        self.assertEqual(recap.public_match(SAMPLE)['warconUrl'],f'{recap.PUBLIC_SITE}/812')
    def test_webhook_is_restricted_to_discord(self):
        with self.assertRaises(ValueError):
            recap.send_discord('https://attacker.example/api/webhooks/1/foo', {})

if __name__=='__main__':unittest.main()
