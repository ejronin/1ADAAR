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


    def test_forecast_contract(self):
        page=(ROOT/'gold.html').read_text(encoding='utf-8')
        js=(ROOT/'js/gold.js').read_text(encoding='utf-8')
        engine=(ROOT/'js/gold-forecast.js').read_text(encoding='utf-8')
        self.assertIn('js/gold-forecast.js?v=1',page)
        self.assertIn('gold-forecast-title',page)
        self.assertIn('rolling historical tests',page)
        self.assertIn('GoldForecast',js)
        for name in ('naive','ses','damped','ar1','momentum'):
            self.assertIn(name,engine)
        self.assertNotIn('fetch(',engine)

    @unittest.skipUnless(shutil.which('node'),'Node.js not installed')
    def test_forecast_walkforward(self):
        expression=r"""
const assert=require('node:assert/strict');
const m=require('./docs/js/gold-forecast.js');
const D=86400000;
const rows=Array.from({length:68},(_,i)=>({
  ts:Date.UTC(2026,7,20)+D*i,
  price:Math.round(500000*Math.exp(i*.02+.30*Math.sin(i*.5)))
}));
const r=m.evaluate(rows);
assert.equal(r.state,'ready');
assert.ok(['naive','ses','damped','ar1','momentum'].includes(r.model));
assert.equal(r.rows.length,7);
assert.ok(r.validations>=14);
assert.equal(r.rows[0].ts,rows[rows.length-1].ts+D);
assert.ok(r.rows.every(x=>x.lower>0&&x.lower<=x.price&&x.price<=x.upper));
assert.ok(m.simulate([100,100,100,100],'naive').every(x=>Math.abs(x-100)<1e-9));
assert.equal(m.evaluate(rows.slice(0,42)).state,'insufficient');
const gapped=rows.slice();gapped.splice(45,1);
assert.equal(m.evaluate(gapped).state,'insufficient');
// Forecast model never receives future data during historical validation;
// first 21 fold origin dates must precede each evaluated outcome.
assert.ok(r.validations<=21);
"""
        process=subprocess.run(['node','-e',expression],cwd=ROOT.parent,
                               capture_output=True,text=True,timeout=12)
        self.assertEqual(process.returncode,0,process.stderr)


    @unittest.skipUnless(shutil.which('node'),'Node.js not installed')
    def test_grouped_daily_candles_use_actual_prices(self):
        expression=r"""
const assert=require('node:assert/strict');
const m=require('./docs/js/gold.js');
const d=86400000;
const values=[100,130,110,75,90,135,95];
const rows=values.map((price,i)=>({ts:i*d,price}));
const candles=m.buildCandles(rows,'7');
assert.equal(m.candleSpan('7',7),2);
assert.equal(m.candleSpan('30',30),3);
assert.equal(m.candleSpan('90',90),7);
assert.equal(candles.length,4);
assert.deepEqual([candles[0].open,candles[0].close,candles[0].high,candles[0].low],[100,100,100,100]);
assert.deepEqual([candles[3].open,candles[3].close,candles[3].high,candles[3].low],[135,95,135,95]);
assert.ok(candles.every(x=>x.low<=x.open&&x.low<=x.close&&x.high>=x.open&&x.high>=x.close));
assert.deepEqual(m.buildCandles([], '30'),[]);
"""
        run=subprocess.run(['node','-e',expression],cwd=ROOT.parent,capture_output=True,text=True,timeout=12)
        self.assertEqual(run.returncode,0,run.stderr)

    def test_mode_switch_and_no_fake_intraday(self):
        page=(ROOT/'gold.html').read_text(encoding='utf-8')
        script=(ROOT/'js/gold.js').read_text(encoding='utf-8')
        css=(ROOT/'assets/gold.css').read_text(encoding='utf-8')
        self.assertIn('data-chart-mode="line"',page)
        self.assertIn('data-chart-mode="candles"',page)
        self.assertIn('OHLC candlesticks use actual',page)
        self.assertIn('data/gold-observations.json',script)
        self.assertIn('.gold-dashboard{align-items:start}',css)


    def test_forecast_follows_balanced_dashboard(self):
        html=(ROOT/'gold.html').read_text(encoding='utf-8')
        css=(ROOT/'assets/gold.css').read_text(encoding='utf-8')
        before,after=html.split('</aside>\n</div>\n<section class="gold-panel gold-forecast-panel"',1)
        self.assertIn('class="gold-sidebar"',before)
        self.assertNotIn('class="gold-forecast-panel"',before)
        self.assertIn('class="gold-forecast-overview"',after)
        self.assertIn('class="gold-forecast-method"',after)
        self.assertLess(html.index('id="gold-forecast-title"'),html.index('id="gold-history-title"'))
        for identifier in ('gold-forecast-1','gold-forecast-7','gold-forecast-model','gold-forecast-backtest'):
            self.assertEqual(html.count('id="'+identifier+'"'),1)
        self.assertIn('.gold-forecast-panel{',css)
        self.assertIn('grid-template-columns:minmax(0,1fr) minmax(0,1.15fr)',css)


    def test_hover_tooltip_uses_svg_screen_transform(self):
        html=(ROOT/'gold.html').read_text(encoding='utf-8')
        js=(ROOT/'js/gold.js').read_text(encoding='utf-8')
        css=(ROOT/'assets/gold.css').read_text(encoding='utf-8')
        self.assertIn('id="gold-tooltip"',html)
        self.assertIn('role="tooltip"',html)
        self.assertIn('svg.getScreenCTM()',js)
        self.assertIn('screen.inverse()',js)
        self.assertIn('svg.onpointermove=showHover',js)
        self.assertNotIn('renderChart(rows,selectedTs,projection,mode,range);',js)
        self.assertIn('.gold-tooltip{',css)
        self.assertIn('pointer-events:none',css)

if __name__=='__main__':
    unittest.main()
