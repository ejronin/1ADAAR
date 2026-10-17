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
assert.equal(tabs.children.length,3);
assert.equal(tabs.children[0].attrs['aria-pressed'],'true');
const details=find(host,n=>n.className==='perf-details');
assert.ok(find(details,n=>n.tag==='table'));
const point=find(plot,n=>n.attrs.role==='button');
assert.ok(point);
point.events.focus();
const inspector=find(host,n=>n.className==='perf-inspector');
assert.match(inspector.textContent,/(K\/D|rolling)/);
tabs.children[1].events.click();
assert.equal(tabs.children[1].attrs['aria-pressed'],'true');
assert.ok(find(host,n=>n.textContent==='Deaths'));
tabs.children[2].events.click();
assert.equal(tabs.children[2].attrs['aria-pressed'],'true');
assert.ok(find(host,n=>n.textContent==='LATEST CAREER K/D'));
const empty=new Node('section');
mount(empty,{key,matches:[],career:[],demo:false});
assert.equal(find(empty,n=>n.className==='perf-empty').hidden,false);
assert.equal(find(empty,n=>n.tag==='svg'),null);
console.log('Responsive chart DOM, accessibility and controls smoke tests passed');
