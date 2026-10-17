'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const code=fs.readFileSync('docs/js/server-status.js','utf8');
const fresh=new Date().toISOString();
const tick=()=>new Promise(resolve=>setImmediate(resolve));
async function simulate(input){
 const elements=new Map();
 for(const id of ['server-status','server-status-label','server-status-players','server-status-map','server-status-updated']){
   elements.set(id,{textContent:'',dataset:{},attributes:{},setAttribute(key,val){this.attributes[key]=val;}});
 }
 const calls=[];
 const doc={visibilityState:'visible',getElementById:id=>elements.get(id)||null,addEventListener:()=>{}};
 const browser={setInterval(fn,interval){calls.push(interval);}};
 const fetch=async()=> input===null?{ok:false}:{ok:true,json:async()=>input};
 vm.runInNewContext(code,{document:doc,window:browser,fetch,Date,Object,Number});
 await tick();
 return {elements,calls};
}
(async()=>{
 const status={schemaVersion:1,checkedAt:fresh,observedAt:fresh,state:'online',players:0,maxPlayers:100,map:'Bakurani'};
 let r=await simulate(status);
 assert.equal(r.elements.get('server-status').dataset.state,'online');
 assert.equal(r.elements.get('server-status-players').textContent,'0 / 100');
 assert.equal(r.elements.get('server-status-map').textContent,'Bakurani');
 assert.deepEqual(r.calls,[120000]);
 r=await simulate({...status,state:'offline',players:null,map:null});
 assert.equal(r.elements.get('server-status').dataset.state,'offline');
 assert.equal(r.elements.get('server-status-players').textContent,'—');
 r=await simulate({...status,state:'reconnecting',players:null,map:null});
 assert.equal(r.elements.get('server-status').dataset.state,'reconnecting');
 r=await simulate({...status,checkedAt:'2020-01-01T00:00:00Z'});
 assert.equal(r.elements.get('server-status').dataset.state,'unknown');
 r=await simulate(null);
 assert.equal(r.elements.get('server-status').dataset.state,'unknown');
 console.log('Server status DOM tests: live, empty, offline, reconnecting, stale, API failure passed.');
})().catch(e=>{console.error(e);process.exitCode=1;});
