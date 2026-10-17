import pathlib
import re
import subprocess
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class RepositorySecurityBaseline(unittest.TestCase):
    def test_sensitive_exports_ignored_by_git(self):
        patterns=[
          'ServerSettings.ini','.env.production','.env.local','credentials.secret',
          'dan.rcon','server.token','wardogs.sqlite','players-export.csv',
          'roster_2026.csv','backup.zip','production-backup.tar.gz','warcon-dump.json',
          '.private/server.json','private/secrets.json'
        ]
        for name in patterns:
            p=subprocess.run(['git','check-ignore','-q','--no-index',name],
                 cwd=ROOT,check=False)
            self.assertEqual(p.returncode,0,name)
    def test_no_sensitive_tracked_paths(self):
        lines=subprocess.check_output(['git','ls-files'],cwd=ROOT,text=True).splitlines()
        bad=[x for x in lines if re.search(
            r'(^|/)(\.env(\.|$)|ServerSettings\.ini$|id_rsa|id_ed25519|\.private/|private/)|'
            r'\.(p12|pfx|pem|key|db|sqlite3?|zip|7z|sql|backup|log)$',x,re.I)]
        # The deliberately empty template is approved and contains no credentials.
        bad=[name for name in bad if name != '.env.example']
        self.assertEqual(bad,[],f'Sensitive files tracked: {bad}')
        example=(ROOT/'.env.example').read_text()
        self.assertNotRegex(example,r'(?im)^[ \t]*[A-Z_][A-Z0-9_]*[ \t]*=[ \t]*[^ \t\r\n#]', 'Example env contains real values')
    def test_public_files_do_not_contain_credential_patterns(self):
        src=ROOT/'docs'
        for path in src.rglob('*'):
            if not path.is_file() or path.suffix.lower() not in {'.html','.css','.json','.svg','.js','.txt'}:continue
            text=path.read_text(encoding='utf-8')
            self.assertNotRegex(text,r'(?i)discord(?:app)?\.com/api/webhooks/\d+/',
                                f'Webhook URL in {path}')
            self.assertNotRegex(text,r'\b(?:wkf|wck)_[A-Za-z0-9_-]{15,}\b',
                                f'WARCON token in {path}')
            self.assertNotRegex(text,r'\b7656119\d{10}\b',
                                f'Raw SteamID in {path}')
    def test_public_player_index_removes_unused_activity_and_cash(self):
        import json
        from src.player_index import sanitize_board_row
        for person in json.loads((ROOT/'docs/data/players.json').read_text())['players']:
            self.assertNotIn('lastSeen',person)
            self.assertNotIn('cash',person)
        sample={"steamId":"76561190000000001","name":"Test","cash":1000,
                "lastSeen":"2026-10-16T21:00:00Z"}
        row=sanitize_board_row(sample,has_feed=False)
        self.assertNotIn('cash',row)
        self.assertNotIn('lastSeen',row)
    def test_public_export_restrictions_documented(self):
        readme=(ROOT/'README.md').read_text()
        self.assertIn('hashed keys are pseudonymous',readme)
        self.assertIn('not truly anonymous',readme)
        self.assertIn('Opening a player profile',readme)
