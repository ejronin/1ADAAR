'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const fixture=JSON.parse(fs.readFileSync('tests/fixtures/demo-player.json','utf-8'));
let rendered=null;
vm.runInNewContext(fs.readFileSync('docs/js/demo-performance.js','utf-8'),{
  window:{OneADAARPerformance:{mount:(_target,data)=>{rendered=data;}}},
  document:{getElementById:id=>({id})}
});
assert.ok(rendered&&rendered.demo);
assert.equal(rendered.key,fixture.player.key);
assert.equal(rendered.matches.length,fixture.matches.length);
for(let i=0;i<rendered.matches.length;i++){
  const a=rendered.matches[i],b=fixture.matches[i];
  assert.equal(a.endedAt,b.endedAt);assert.equal(a.map,b.map);
  assert.equal(a.players[0].kills,b.players[0].kills);
  assert.equal(a.players[0].deaths,b.players[0].deaths);
}
assert.equal(rendered.career.length,fixture.careerHistory.length);
for(let i=0;i<rendered.career.length;i++){
  for(const field of ['date','kills','deaths','matches','wins','losses','draws','minutes'])
    assert.equal(rendered.career[i][field],fixture.careerHistory[i][field]);
}
console.log('PlayerOne synthetic chart / fixture parity passed.');
