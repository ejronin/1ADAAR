"""GOLD is a separate, sourced, public market page. No account or notification changes."""
import json
import shutil
import subprocess
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]/'docs'
PAGES=('index.html','seasons.html','players.html','map-team.html',
       'activity.html','progression.html','compare.html','weekly.html','gold.html')

class GoldPageTests(unittest.TestCase):
    def test_gold_is_reachable_from_all_navigation(self):
        for page in PAGES:
            html=(ROOT/page).read_text(encoding='utf-8')
            with self.subTest(page=page):
                self.assertEqual(html.count('href="gold.html"'),1)
        gold=(ROOT/'gold.html').read_text(encoding='utf-8')
        self.assertIn('aria-current="page"',gold)
        self.assertIn('assets/gold.css?v=1',gold)
        self.assertIn('js/gold.js?v=1',gold)

    def test_source_credit_and_no_fake_forecasting(self):
        page=(ROOT/'gold.html').read_text(encoding='utf-8')
        js=(ROOT/'js/gold.js').read_text(encoding='utf-8')
        self.assertIn('https://wardogserverlist.com/gold-bars',page)
        self.assertIn('https://creativecommons.org/licenses/by/4.0/',page)
        self.assertIn('Historical range, not a price forecast',page)
        self.assertIn('https://wardogserverlist.com/api/gold-bars',js)
        self.assertIn("if(!response.ok)throw",js)
        self.assertNotIn('Discord',page)
        self.assertNotIn('notification',page.lower())

    @unittest.skipUnless(shutil.which('node'),'Node.js not installed')
    def test_daily_math_and_missing_day_handling(self):
        expression=r"""
const assert=require('node:assert/strict');
const g=require('./docs/js/gold.js');
const d=86400000;
const rows=[{ts:0,price:100},{ts:d,price:110},{ts:d*7,price:80}];
assert.deepEqual(g.sliceDays(rows,7),rows.slice(1));
assert.equal(g.diffDays(rows,1),null);
assert.equal(g.diffDays(rows,7),-20);
assert.equal(g.average(rows),97);
assert.equal(g.changeText(null),'—');
assert.equal(g.changeText(-12.34),'-12.3%');
assert.throws(()=>g.normalize({points:[[0,-2]]}));
assert.deepEqual(g.normalize({points:[[d,110],[0,100],[d,111],[30,2]]}).rows,
    [{ts:0,price:100},{ts:d,price:111}]);
"""
        process=subprocess.run(['node','-e',expression],cwd=ROOT.parent,
                               capture_output=True,text=True,timeout=12)
        self.assertEqual(process.returncode,0,process.stderr)

if __name__=='__main__':
    unittest.main()
