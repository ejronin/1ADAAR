"""Optional Steam PFP enrichment: safe source, privacy, cache and failure behavior."""
import datetime as dt
import json
import unittest
from pathlib import Path

from src.player_index import collect_players, player_key
from src.steam_avatars import resolve_avatars, valid_avatar_url

SID1 = "76561190000000001"
SID2 = "76561190000000002"
HASH = "ab" * 20
URL = "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ab/" + HASH + "_full.jpg"
NOW = dt.datetime(2026, 10, 20, 20, 0, tzinfo=dt.timezone.utc)


class SteamAvatarTests(unittest.TestCase):
    def test_allow_only_documented_steam_avatar_cdn_urls(self):
        self.assertEqual(valid_avatar_url(URL), URL)
        modern = "https://avatars.akamai.steamstatic.com/" + HASH + "_full.jpg"
        self.assertEqual(valid_avatar_url(modern), modern)
        for invalid in (
            "http:" + URL[6:], URL + "?tracker=1",
            "https://steamcdn-a.akamaihd.net.evil.test/steamcommunity/public/images/avatars/ab/" + HASH + "_full.jpg",
            "https://cdn.evil.test/" + HASH + "_full.jpg",
            "javascript:alert(1)", "data:image/svg+xml,x",
            "https://steamcdn-a.akamaihd.net/steamcommunity/public/images/avatars/ab/../" + HASH + "_full.jpg",
            "https://avatars.steamstatic.com/" + HASH + "_medium.jpg",
            "https://avatars.steamstatic.com/" + SID1 + "_full.jpg",
            None,
        ):
            with self.subTest(url=invalid):
                self.assertIsNone(valid_avatar_url(invalid))

    def test_backend_joins_by_steamid_not_persona_name(self):
        calls = []
        def fetch(ids, key):
            calls.append((ids, key))
            return {"response": {"players": [
                {"steamid": SID2, "personaname": "Same Name", "avatarfull": URL},
                {"steamid": SID1, "personaname": "Same Name", "avatarfull": "http://bad.test/pfp.jpg"},
                {"steamid": "76561190000000099", "avatarfull": URL},
            ]}}
        ids = {player_key(SID1): SID1, player_key(SID2): SID2}
        got = resolve_avatars(ids, [], "dummy-key", now=NOW, fetch=fetch)
        self.assertEqual(calls, [([SID1, SID2], "dummy-key")])
        self.assertNotIn("avatar", got[player_key(SID1)])
        self.assertEqual(got[player_key(SID2)]["avatar"], URL)
        self.assertEqual(got[player_key(SID1)]["avatarCheckedAt"], "2026-10-20T20:00:00Z")
        self.assertNotIn(SID1, json.dumps(got))
        self.assertNotIn("dummy-key", json.dumps(got))

    def test_cache_is_24_hours_and_missing_key_uses_last_good_avatar(self):
        previous = [{
            "key": player_key(SID1), "avatar": URL,
            "avatarCheckedAt": "2026-10-20T02:00:00Z",
        }]
        def fail(*_):
            raise AssertionError("Must not hit Steam within refresh window")
        got = resolve_avatars({player_key(SID1): SID1}, previous, "dummy-key",
                              now=NOW, fetch=fail)
        self.assertEqual(got[player_key(SID1)]["avatar"], URL)
        later = NOW + dt.timedelta(days=2)
        got = resolve_avatars({player_key(SID1): SID1}, previous, "",
                              now=later, fetch=fail)
        self.assertEqual(got[player_key(SID1)]["avatar"], URL)
        self.assertNotIn("avatarCheckedAt", got[player_key(SID1)])

    def test_steam_failure_never_erases_existing_valid_avatar(self):
        previous = [{"key": player_key(SID1), "avatar": URL,
                     "avatarCheckedAt": "2026-10-16T00:00:00Z"}]
        got = resolve_avatars({player_key(SID1): SID1}, previous, "dummy-key",
                              now=NOW, fetch=lambda *_: (_ for _ in ()).throw(TimeoutError()))
        self.assertEqual(got[player_key(SID1)]["avatar"], URL)

    def test_sanitized_index_never_contains_raw_ids_or_api_key(self):
        rows = [{
            "steamId": SID1, "name": "Same Name", "rank": 1,
            "matches": 10, "wins": 6, "losses": 4, "deaths": 50, "kills": 100
        }]
        def board(_):
            return {"total": 1, "rows": rows, "hasFeed": False}
        def avatars(raw_ids):
            self.assertEqual(raw_ids, {player_key(SID1): SID1})
            return {player_key(SID1): {"avatar": URL}}
        public = collect_players(board, "https://example.invalid/leaderboard",
                                 avatar_resolver=avatars)
        self.assertEqual(public["players"][0]["avatar"], URL)
        self.assertNotIn(SID1, json.dumps(public))
        self.assertNotIn("steamId", json.dumps(public))

    def test_ui_uses_image_loading_and_initial_fallback(self):
        src = Path(__file__).resolve().parents[1] / "docs"
        markup = (src / "players.html").read_text()
        js = (src / "js" / "players.js").read_text()
        self.assertIn("id=\"profile-avatar-image\"", markup)
        self.assertIn("id=\"profile-avatar-fallback\"", markup)
        self.assertIn("showSteamPortrait(entry)", js)
        self.assertIn("validSteamAvatar(entry.avatar)", js)
        self.assertIn("img.onerror", js)
        self.assertIn("profile-avatar-fallback", js)


if __name__ == "__main__":
    unittest.main()
