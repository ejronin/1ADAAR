import json
import unittest
from pathlib import Path
from unittest.mock import patch
from src import player_index, recap

SID = '76561190000000001'
BOARD_ROW = {'steamId':SID,'name':'1AD TestRunner','rank':1,'minutes':180,'seedMinutes':20,
             'kills':24,'deaths':12,'matches':3,'wins':2,'losses':1,'draws':0,'cash':5000,
             'headshots':5,'vehicleKills':2,'killStreak':4,'lastSeen':'2026-10-16T00:00:00Z'}

class TestPlayerIndex(unittest.TestCase):
    def test_steamid_lookups_are_one_way_and_consistent(self):
        key=player_index.player_key(SID)
        self.assertEqual(len(key),64)
        self.assertNotIn(SID,key)
        self.assertEqual(key,player_index.player_key(SID))
        self.assertEqual(player_index.player_key('7656119'), '')
        self.assertEqual(player_index.player_key('12345678901234567EXTRA'),'')
    def test_row_public_stats_have_no_raw_identifier(self):
        row=player_index.sanitize_board_row(BOARD_ROW,has_feed=True)
        self.assertEqual(row['name'],'1AD TestRunner')
        self.assertEqual(row['kills'],24)
        self.assertEqual(row['rank'],1)
        self.assertEqual(row['headshots'],5)
        self.assertNotIn('lastSeen', row)
        self.assertNotIn('cash', row)
        self.assertNotIn('steamId',json.dumps(row))
        self.assertNotIn(SID,json.dumps(row))
    def test_feed_metrics_not_displayed_before_feed(self):
        row=player_index.sanitize_board_row(BOARD_ROW,has_feed=False)
        self.assertIsNone(row['headshots'])
        self.assertIsNone(row['killStreak'])
    def test_never_publish_steamid_as_fallback_name(self):
        self.assertIsNone(player_index.sanitize_board_row({**BOARD_ROW,'name':SID},has_feed=False))
        self.assertEqual(player_index.safe_name('@everyone Alice'), 'everyone Alice')
    def test_first_page_and_pagination(self):
        def fake(url):
            self.assertIn('/leaderboard?',url)
            return {'ok':True,'total':1,'hasFeed':True,'rows':[BOARD_ROW]}
        res=player_index.collect_players(fake,recap.PUBLIC_BOARD)
        self.assertEqual(len(res['players']),1)
        self.assertEqual(res['players'][0]['rank'],1)
        self.assertFalse(res['capped'])
    def test_match_lines_join_to_public_index_without_id(self):
        summary={'id':12,'startedAt':'2026-10-14T20:00:00Z','endedAt':'2026-10-14T20:47:00Z',
                 'map':'Kavkazi','experiences':'Bakurani_KOTH_01','peakPlayers':20,
                 'finalScores':[{'name':'Lonestar','score':100},{'name':'Valkyra','score':90}], 'winner':'Lonestar'}
        detail={'hasFeed':True,'lines':[{'steamId':SID,'name':'1AD TestRunner','faction':'Lonestar','kills':24,
                 'deaths':12,'seconds':1800,'cashDelta':700,'result':'win','headshots':5,'longestM':400,'killStreak':4}]}
        m=recap.public_match(summary,detail)
        self.assertEqual(m['players'][0]['key'],player_index.player_key(SID))
        self.assertEqual(m['players'][0]['result'],'win')
        self.assertNotIn(SID,json.dumps(m))
        self.assertNotIn('steamId',json.dumps(m))
    def test_dashboard_only_shows_approved_metrics(self):
        base=Path(__file__).resolve().parents[1]/'docs'
        text=(base/'players.html').read_text()+(base/'js'/'players.js').read_text()
        self.assertNotIn('Steam profile ↗',text)
        self.assertNotIn('accuracyRate',text)
        self.assertNotIn('revives',text)
        self.assertIn('Name',text)
        self.assertIn('crypto.subtle.digest',text)
        self.assertIn('p.key===',text)
        self.assertIn('players.html', (base/'index.html').read_text())
        self.assertNotIn('GRID // 1AD', (base/'index.html').read_text())
