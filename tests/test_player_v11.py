"""Approved v1.1.0 UX contract, private Steam avatar matching and feature parity."""
from __future__ import annotations
import json
from pathlib import Path
from unittest.mock import patch
import unittest

from src.player_index import collect_players, player_key
from src.steam_avatars import fetch_steam_avatars, safe_avatar

ROOT=Path(__file__).resolve().parents[1]
DOCS=ROOT/"docs"
SID="76561190000000001"
OTHER="76561190000000002"
AVATAR="https://avatars.steamstatic.com/a0b1c2d3e4f5_full.jpg"


class AvatarSafeTests(unittest.TestCase):
    def test_only_real_steam_cdn_portrait_urls_accepted(self):
        self.assertEqual(safe_avatar(AVATAR),AVATAR)
        self.assertIsNone(safe_avatar("https://example.invalid/portrait.jpg"))
        self.assertIsNone(safe_avatar("http://avatars.steamstatic.com/a.jpg"))
        self.assertIsNone(safe_avatar("https://avatars.steamstatic.com.evil.com/a.jpg"))
        self.assertIsNone(safe_avatar("javascript:alert(1)"))
        self.assertIsNone(safe_avatar("https://avatars.steamstatic.com/../secret.png?evil=<script>"))

    def test_collector_maps_exact_steamid_to_existing_pseudonymous_key(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):return False
            def read(self,n):
                return json.dumps({"response":{"players":[
                    {"steamid":OTHER,"avatarfull":AVATAR},
                    {"steamid":SID,"avatarfull":AVATAR},
                    {"steamid":SID,"avatarfull":"https://not-steam.example/evil.jpg"}
                ]}}).encode()
            def geturl(self):
                return "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key=dummy"
        with patch("src.steam_avatars.urllib.request.urlopen",return_value=Response()):
            resolved=fetch_steam_avatars({player_key(SID):SID},"a"*32)
        self.assertEqual(resolved,{player_key(SID):AVATAR})
        self.assertNotIn(OTHER,json.dumps(resolved))
        self.assertNotIn(SID,json.dumps(resolved))

    def test_public_index_stays_without_steamids_when_avatar_present(self):
        response=lambda url:{"ok":True,"hasFeed":False,"total":1,"rows":[{
            "steamId":SID,"name":"Real Example","rank":4,"matches":13,"wins":6,
            "losses":6,"draws":1,"kills":90,"deaths":71}]}
        def avatar(ids):
            self.assertEqual(ids,{player_key(SID):SID})
            return {player_key(SID):AVATAR,player_key(OTHER):"https://www.evil.invalid/3.jpg"}
        board=collect_players(response,"https://console.warcon.app/api/public/servers/test/leaderboard",avatar_lookup=avatar)
        serialized=json.dumps(board)
        self.assertNotIn(SID,serialized)
        self.assertNotIn("steamId",serialized)
        self.assertNotIn("api_key",serialized)
        self.assertEqual(board["players"][0]["avatar"],AVATAR)

    def test_invalid_avatar_lookup_fails_closed(self):
        lookup=lambda _:{"extra":'https://evil.test/a.jpg'}
        response=lambda _:{"rows":[{"steamId":SID,"name":"Example","rank":1}],"total":1}
        board=collect_players(response,"https://console.warcon.app/api/public/servers/test/leaderboard",avatar_lookup=lookup)
        self.assertNotIn("avatar",board["players"][0])


class LayoutContractTests(unittest.TestCase):
    def test_seven_cards_one_donut_two_bars_and_exact_chart_modes(self):
        html=(DOCS/"players.html").read_text()
        for marker in ('id="profile-metrics"','id="profile-secondary"',
                       'id="player-snapshot"','id="player-avatar"',
                       'id="combat-metrics"','id="map-breakdown"','id="faction-breakdown"',
                       'id="recent-match-table"','id="map-team-details"'):
            self.assertIn(marker,html)
        snap=(DOCS/"js/player-snapshot.js").read_text()
        self.assertIn("Career win rate",snap)
        self.assertIn("Most-played faction",snap)
        self.assertIn("Most-played map",snap)
        self.assertIn("'donut-'+type",snap)
        self.assertIn(".donut-progress",(DOCS/"assets/player-v11.css").read_text())
        self.assertIn("Participation, not win rate",snap)
        self.assertIn("steam-avatar",snap)
        self.assertIn("textContent",snap)
        self.assertNotIn("innerHTML",snap)
        js=(DOCS/"js/performance.js").read_text()
        for label in ("Kills & deaths","K/D per match","Trailing 5-match K/D","Trailing 5-match averages","Career K/D history",
                      "Last 10","Last 20","All available","See the numbers in a table"):
            self.assertIn(label,js)
        self.assertIn("color:'#86f4a4'",js)
        self.assertIn("color:'#f5c84b'",js)
        self.assertIn("tabindex:'0'",js)
        self.assertIn("POINTS SHOWN",js)
        self.assertIn("oldest to newest",js.lower())
        self.assertIn("five consecutive saved matches",js.lower())
        self.assertIn("perf-explanation",js)
        self.assertIn('href="activity.html"',html)
        self.assertIn("prefers-reduced-motion",(DOCS/"assets/player-v11.css").read_text())
        release=(ROOT/"planning/V1.1.0_RELEASE_GATES.md").read_text()
        self.assertIn("one career win-rate SVG donut",release)
        self.assertNotIn("three distinct SVG donut graphs",release)
        self.assertIn("one most-played faction insight",release)

    def test_fictional_playerone_totals_and_share_bars_are_original_fixture(self):
        data=json.loads(((Path(__file__).resolve().parents[1]/'tests/fixtures/demo-player.json')).read_text())
        page=((Path(__file__).resolve().parents[1]/'tests/fixtures/playerone-demo.html')).read_text()
        self.assertTrue(data["fictional"])
        p=data["player"]
        self.assertEqual((p["kills"],p["deaths"],p["wins"],p["matches"]),(634,332,27,48))
        self.assertIn("27 wins / 48 career results",page)
        self.assertIn("4 of 10 recent appearances · 40%",page)
        self.assertIn("stroke-dasharray=\"56.25 100\"",page)
        self.assertIn("SAMPLE PLAYER — MADE-UP STATS",page)
        self.assertIn("Team kills",page)
        self.assertEqual(page.count("<tr>"),11)
        self.assertNotIn("demo-playerone",(DOCS/"data/players.json").read_text())

if __name__=="__main__":
    unittest.main()
