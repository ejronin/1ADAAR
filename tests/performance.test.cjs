'use strict';
const assert=require('node:assert/strict');
const M=require('../docs/js/performance-core.js');
const key='a'.repeat(64);
function match(id,date,k,d){
  return {id,endedAt:'2026-10-'+date+'T14:00:00Z',map:'Bakurani',
    players:[{key,kills:k,deaths:d}]};
}
const rows=[
  match(1,'01',10,5),match(2,'02',8,4),match(3,'03',0,0),
  match(4,'04',6,0),match(5,'05',20,10),match(6,'06',15,5)
];
const series=M.matchSeries(rows.slice().reverse(),key);
assert.deepEqual(series.map(x=>x.id),['1','2','3','4','5','6']);
assert.equal(series[0].kd,2);
assert.equal(series[2].kd,null);
assert.equal(series[3].kd,6);
assert.equal(series[0].rolling,null);
assert.equal(series[4].rolling,2.32); // (10+8+0+6+20)/(5+4+0+0+10) = 44/19
assert.equal(series[4].avgKills,8.8);
assert.equal(series[4].avgDeaths,3.8);
assert.equal(series[0].avgKills,null);
assert.equal(series[5].avgKills,9.8);
assert.equal(series[5].avgDeaths,3.8);
assert.equal(series[5].rolling,2.58); // (8+0+6+20+15)/(4+0+0+10+5) = 49/19
assert.equal(M.windowed(series,10).length,6);
assert.equal(M.windowed(series,25).length,6);
assert.equal(M.windowed(Array.from({length:30},(_,i)=>i),10).length,10);
assert.equal(M.windowed(Array.from({length:30},(_,i)=>i),25).length,25);
assert.equal(M.windowed(series,Infinity).length,6);
assert.equal(M.matchSeries([...rows,rows[0]],key).length,6);
assert.equal(M.matchSeries(rows,'does-not-exist').length,0);
const career=M.careerSeries([
 {date:'2026-10-03',kills:22,deaths:12,matches:3,wins:1},
 {date:'2026-10-02',kills:18,deaths:9,matches:2,wins:1},
 {date:'2026-10-03',kills:24,deaths:12,matches:3,wins:2},
 {date:'2026-10-05',kills:-2,deaths:12,matches:5,wins:2}
]);
assert.equal(career.length,2);
assert.equal(career[1].kd,2);
assert.equal(career[0].kd,2);
console.log('Performance math / history / missing-data regression checks passed');
