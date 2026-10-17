'use strict';
const assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const sort=require('../docs/js/match-sort.js');
class Node{
  constructor(tag){this.tag=tag;this.children=[];this.attrs={};this.events={};this.dataset={};
    this.style={setProperty(){}};this.textContent='';this.hidden=false;this.disabled=false;this.value='';this.className='';}
  append(...children){this.children.push(...children);}
  replaceChildren(...children){this.children=[...children];}
  setAttribute(k,v){this.attrs[k]=v;}
  addEventListener(k,fn){this.events[k]=fn;}
}
const ids=new Map();
const $=id=>{if(!ids.has(id))ids.set(id,new Node('div'));return ids.get(id);};
const matches=[{id:3,map:'Ozeti',winner:'Valkyra',endedAt:'2026-10-13T19:00:00Z',
 durationSeconds:3600,peakPlayers:20,scores:[{name:'Valkyra',score:100}]},
 {id:1,map:'Bakurani',winner:'Lonestar',endedAt:'2026-10-11T19:00:00Z',
 durationSeconds:3600,peakPlayers:20,scores:[{name:'Lonestar',score:100}]},
 {id:2,map:'Zestafona',winner:'Manticore',endedAt:'2026-10-12T19:00:00Z',
 durationSeconds:3600,peakPlayers:20,scores:[{name:'Manticore',score:100}]}];
const document={getElementById:$,createElement:tag=>new Node(tag),createTextNode:val=>({textContent:val})};
const context={document,window:{OneADAARArchive:sort,OneADAARFactions:{
  label: name=>{const n=new Node('span');n.textContent=name;return n;},
  identify:()=>null
}},location:{pathname:'/1ADAAR/index.html',hash:''},
 history:{replaceState(){}},
 fetch:async()=>({ok:true,json:async()=>({matches,lastCheckedAt:'2026-10-16T12:00:00Z'})}),
 URL,Date};
vm.runInNewContext(fs.readFileSync('docs/js/app.js','utf8'),context);
const flush=()=>new Promise(resolve=>setImmediate(resolve));
function order(){return $('match-grid').children.map(n=>n.attrs['aria-label']);}
(async()=>{
 await flush();
 assert.equal($('sort-matches').disabled,false);
 assert.ok(order()[0].includes('match 3'));
 const select=$('sort-matches');
 select.events.change({target:{value:'oldest'}});
 assert.ok(order()[0].includes('match 1'));
 assert.match($('sort-explanation').textContent,/Oldest first/);
 select.events.change({target:{value:'newest'}});
 assert.ok(order()[0].includes('match 3'));
 $('find-match').events.input({target:{value:'Ozeti'}});
 assert.equal(select.disabled,true);
 assert.equal(order().length,1);
 $('find-match').events.input({target:{value:''}});
 assert.equal(select.disabled,false);
 console.log('Archive dropdown integration changes real card order and disables with one result.');
})().catch(e=>{console.error(e);process.exitCode=1;});
