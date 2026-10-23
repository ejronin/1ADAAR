'use strict';
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const window={};
vm.runInNewContext(fs.readFileSync('docs/js/role-radar.js','utf8'),{window,document:{}});
const scale=window.OneADAARRoleRadar.scaleFor;
function levels(...xs){
 const keys=window.OneADAARRoleRadar.ROLES;
 return Object.fromEntries(keys.map((name,i)=>[name,xs[i]||0]));
}
assert.equal(scale(levels(5,6,6,0,0,0)),10);
assert.equal(scale(levels(5,13,25,6,15,20)),30);
assert.equal(scale(levels(44,41,38,9,11,20)),50);
assert.equal(scale(levels(0,0,0,0,0,0)),10);
assert.equal(scale(levels(100,100,100,100,100,100)),100);
assert.equal(scale(levels(0,1,0,0,0,0)),10);
console.log('Dynamic radar display scale passes six genuine account examples.');
