'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const root=path.join(__dirname,'..'),info=JSON.parse(fs.readFileSync(path.join(root,'BUILD_INFO.json'),'utf8'));
test('dashboard and mobile assets use one version so old bare JavaScript URLs are not reused',()=>{
 for(const name of ['index.html','mobile.html']){
  const html=fs.readFileSync(path.join(root,name),'utf8');
  const scripts=[...html.matchAll(/<script[^>]+src="([^"]+)"/g)].map(m=>m[1]);assert.ok(scripts.length>=4);
  for(const src of scripts){assert.equal(new URLSearchParams(src.split('?')[1]).get('v'),info.build_id,src);assert.ok(fs.existsSync(path.join(root,src.split('?')[0])));}
  for(const match of html.matchAll(/<link[^>]+href="([^"]+\.css[^"]*)"/g))assert.equal(new URLSearchParams(match[1].split('?')[1]).get('v'),info.build_id);
 }
});
test('all direct dashboard event targets exist exactly once in the shipped HTML',()=>{
 const html=fs.readFileSync(path.join(root,'index.html'),'utf8'),app=fs.readFileSync(path.join(root,'app.js'),'utf8');
 const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length,'No duplicate IDs');
 for(const m of app.matchAll(/\$\('([^']+)'\)\.addEventListener/g))assert.ok(ids.includes(m[1]),'Missing event target #'+m[1]);
});
test('generated offline preview contains the same build and no external script or stylesheet dependency',()=>{
 const html=fs.readFileSync(path.join(root,'START_HERE.html'),'utf8');assert.ok(html.includes(info.build_id));assert.doesNotMatch(html,/<script[^>]+src=|<link[^>]+href=/);assert.match(html,/window.MOULDSHIELD_STANDALONE=true/);assert.match(html,/function switchDataMode/);
});
