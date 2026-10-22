'use strict';
/* Tiny DOM simulation catches chart construction and controls without network/packages. */
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm');
const core=require('../docs/js/performance-core.js');
class Node {
  constructor(tag){
    this.tag=tag;this.children=[];this.events={};this.style={};this.attrs={};
    this.dataset={};this.className='';this.textContent='';this.value='';this.hidden=false;
  }
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.children=[...nodes];this.textContent='';}
  setAttribute(name,value){this.attrs[name]=String(value);}
  addEventListener(event,callback){this.events[event]=callback;}
  querySelector(){return null;}
}
const document={
  createElement:tag=>new Node(tag),
  createElementNS:(_ns,tag)=>new Node(tag),
  createTextNode:text=>({textContent:text})
};
const window={OneADAARMetrics:core};
vm.runInNewContext(fs.readFileSync('docs/js/performance.js','utf8'),{document,window});
const mount=window.OneADAARPerformance.mount;
const key='a'.repeat(64);
const m=i=>({id:i,endedAt:'2026-10-'+String(i).padStart(2,'0')+'T19:00:00Z',
  map:'Bakurani',players:[{key,kills:i*4,deaths:i+1}]});
function find(root,callback){
  if(callback(root))return root;
  for(const n of root.children||[]){const found=find(n,callback);if(found)return found;}
  return null;
}
const host=new Node('section');
mount(host,{key,matches:[1,2,3,4,5,6].map(m),career:[
  {date:'2026-10-04',kills:80,deaths:40,matches:4,wins:2},
  {date:'2026-10-06',kills:110,deaths:55,matches:6,wins:4}
],demo:false});
const plot=find(host,n=>n.className==='perf-canvas');
assert.ok(plot);
assert.ok(find(plot,n=>n.tag==='svg'));
const tabs=find(host,n=>n.className==='perf-tabs');
assert.equal(tabs.children.length,5);
assert.match(find(host,n=>n.className==='perf-explanation').textContent,/single match/);
assert.match(find(host,n=>n.className==='perf-window-label').textContent,/POINTS SHOWN/);
assert.equal(tabs.children[1].attrs['aria-pressed'],'true');
const details=find(host,n=>n.className==='perf-details');
assert.ok(find(details,n=>n.tag==='table'));
const point=find(plot,n=>n.attrs.role==='button');
assert.ok(point);
point.events.focus();
const inspector=find(host,n=>n.className==='perf-inspector');
assert.match(inspector.textContent,/(K\/D|Last 5 matches)/);
tabs.children[0].events.click();
assert.equal(tabs.children[0].attrs['aria-pressed'],'true');
assert.ok(find(host,n=>n.textContent==='Deaths'));
tabs.children[2].events.click();
assert.equal(tabs.children[2].attrs['aria-pressed'],'true');
assert.match(find(host,n=>n.className==='perf-explanation').textContent,/four preceding saved matches/);
assert.match(find(host,n=>n.className==='perf-explanation').textContent,/Last 10 points/);
assert.ok(find(host,n=>n.textContent==='Rolling K/D (5 matches)'));
tabs.children[4].events.click();
assert.equal(tabs.children[4].attrs['aria-pressed'],'true');
assert.ok(find(host,n=>n.textContent==='LATEST CAREER K/D'));
const empty=new Node('section');
mount(empty,{key,matches:[],career:[],demo:false});
assert.equal(find(empty,n=>n.className==='perf-empty').hidden,false);
assert.equal(find(empty,n=>n.tag==='svg'),null);
console.log('Responsive chart DOM, accessibility and controls smoke tests passed');

const twelveMonthDays=Array.from({length:32},(_,i)=>new Date(Date.UTC(2026,8,13+i)).toISOString().slice(0,10));
const chronological=twelveMonthDays.map((day,i)=>({
  id:i+1,endedAt:day+'T19:00:00Z',map:'Bakurani',
  players:[{key,kills:8+i,deaths:2+(i%9)}]
}));
const careerThirtyTwo=twelveMonthDays.map((date,i)=>({
  date,kills:100+i*15,deaths:42+i*7,matches:17+i,wins:9+Math.floor(i/2)
}));
const fullHost=new Node('section');
mount(fullHost,{key,matches:chronological,career:careerThirtyTwo,demo:true});
const select=find(fullHost,n=>n.className==='perf-window');
const coverage=find(fullHost,n=>n.className==='perf-coverage');
const graphic=find(fullHost,n=>n.tag==='svg');
assert.ok(select&&!select.disabled,'Range selector must be enabled with 32 observations');
assert.equal(select.value,'10');
assert.match(coverage.textContent,/10 of 32 saved completed-match records/);
assert.match(graphic.attrs['aria-label'],/10 observations/);
select.value='20';select.events.change();
assert.equal(select.value,'20');
assert.match(coverage.textContent,/20 of 32 saved completed-match records/);
assert.match(find(fullHost,n=>n.tag==='svg').attrs['aria-label'],/20 observations/);
select.value='all';select.events.change();
assert.equal(select.value,'all');
assert.match(coverage.textContent,/32 of 32 saved completed-match records/);
assert.match(find(fullHost,n=>n.tag==='svg').attrs['aria-label'],/32 observations/);
const updatedTable=find(fullHost,n=>n.tag==='tbody');
assert.equal(updatedTable.children.length,32,'Exact data table must change with selected range');
const richTabs=find(fullHost,n=>n.className==='perf-tabs');
richTabs.children[0].events.click();
assert.ok(find(fullHost,n=>n.textContent==='KILLS IN VIEW'));
const killsView=find(fullHost,n=>n.className==='perf-summary');
assert.equal(killsView.children[1].children[1].textContent,
  String(chronological.reduce((sum,row)=>sum+row.players[0].kills,0)));
select.value='10';select.events.change();
const tenKills=chronological.slice(-10).reduce((sum,row)=>sum+row.players[0].kills,0);
assert.equal(killsView.children[1].children[1].textContent,String(tenKills));
richTabs.children[2].events.click();
assert.match(coverage.textContent,/10 of 32 saved completed-match records/);
richTabs.children[4].events.click();
assert.match(coverage.textContent,/10 of 32 saved career snapshots/);
select.value='20';select.events.change();
assert.match(coverage.textContent,/20 of 32 saved career snapshots/);
select.value='all';select.events.change();
assert.match(coverage.textContent,/32 of 32 saved career snapshots/);
const midHost=new Node('section');
mount(midHost,{key,matches:chronological.slice(0,17),career:[],demo:false});
const midSelect=find(midHost,n=>n.className==='perf-window');
assert.equal(midSelect.disabled,false);
assert.equal(midSelect.children[1].disabled,true,'Last 20 and All are duplicates for 17 records');
midSelect.value='all';midSelect.events.change();
assert.match(find(midHost,n=>n.className==='perf-coverage').textContent,/17 of 17/);
assert.equal(find(host,n=>n.className==='perf-window').disabled,true,
 'A real profile with six matches cannot present three indistinguishable ranges');
console.log('32-observation chart selection, reactive summaries, career ranges and sparse-data controls passed.');
