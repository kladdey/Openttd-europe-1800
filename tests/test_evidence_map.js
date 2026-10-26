// Dependency-free smoke test of generated map data and search/layer interactions.
// A minimal DOM exercises logic; this is not a browser rendering/accessibility test.
'use strict';
const fs=require('node:fs'), vm=require('node:vm'), assert=require('node:assert/strict');
const html=fs.readFileSync(process.argv[2]||'maps/calibration/geography_v9/visualization/evidence_map.html','utf8');
const dataset=html.match(/<script id="dataset" type="application\/json">([\s\S]*?)<\/script>/)[1];
const script=html.match(/<script>\s*([\s\S]*?)<\/script>/)[1];
class Element {
 constructor(tag){this.tagName=tag;this.children=[];this.style={};this.attrs={};this.events={};this.textContent='';}
 append(...nodes){this.children.push(...nodes);}setAttribute(k,v){this.attrs[k]=v;}
 addEventListener(k,f){this.events[k]=f;}replaceChildren(){this.children=[];}
 getScreenCTM(){return {a:1,inverse(){return this;}};}setPointerCapture(){}
 createSVGPoint(){return {x:0,y:0,matrixTransform(){return this;}};}
}
const ids={};for(const id of ['map','info','legend','towns','checks','landmarks','reset','search','results','dataset'])ids[id]=new Element(id);
ids.dataset.textContent=dataset;
const document={getElementById:id=>ids[id],createElement:tag=>new Element(tag),createElementNS:(_,tag)=>new Element(tag),createTextNode:text=>({textContent:text})};
vm.runInNewContext(script,{document,console});
const data=JSON.parse(dataset);
const summary=process.argv[3]?JSON.parse(fs.readFileSync(process.argv[3],'utf8')):null;
const expectedTerrain=summary?0:54, expectedInBoundsDeferred=summary?summary.total_deferred-24:12;
assert.equal(data.all.length,600);assert.equal(data.points.length,576);assert.equal(ids.towns.children.length,576);
assert.equal(ids.checks.children.length,21);
assert.equal(data.points.filter(p=>p.evidence_status==='TERRAIN_REVIEW_OPEN').length,expectedTerrain);
assert.equal(data.points.filter(p=>p.evidence_status==='DEFERRED').length,expectedInBoundsDeferred);
ids.search.events.input({target:{value:'LONDON'}});assert.equal(ids.results.children.length,1);
ids.results.children[0].onclick();assert.match(ids.info.textContent,/LONDON/);assert.match(ids.info.textContent,/Founding: untested/);
const outside=data.all.find(p=>!p.x);assert.ok(outside);
ids.search.events.input({target:{value:outside.name}});
const button=ids.results.children.find(b=>b.textContent===outside.name+' (deferred)');assert.ok(button);button.onclick();assert.match(ids.info.textContent,/No in-bounds target/);
const terrainLabel=ids.legend.children[1], cb=terrainLabel.children[0];cb.checked=false;cb.events.change();
const terrainPointIndex=data.points.findIndex(p=>p.evidence_status==='TERRAIN_REVIEW_OPEN');if(terrainPointIndex>=0)assert.equal(ids.towns.children[terrainPointIndex].style.display,'none');
if(summary)assert.equal(data.points.filter(p=>p.evidence_status!=='DEFERRED').length,summary.clear_target_candidate);
ids.landmarks.events.change({target:{checked:false}});assert.equal(ids.checks.style.display,'none');
ids.reset.onclick();assert.equal(ids.map.attrs.viewBox,'0 0 4096 4096');
console.log('PASS: map counts, search, out-of-map deferral, layer toggles and reset');
