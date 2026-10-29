'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..'),source=fs.readFileSync(path.join(root,'app.js'),'utf8');
const coreScripts=['config.js','core.js','phone-core.js'].map(n=>fs.readFileSync(path.join(root,n),'utf8'));
const libs=vm.createContext({window:{},URL});coreScripts.slice(0,3).forEach(s=>vm.runInContext(s,libs));
function load(){const nodes=new Map();const node=id=>{if(!nodes.has(id))nodes.set(id,{hidden:false,textContent:''});return nodes.get(id);};
 const context=vm.createContext({window:{MouldShieldCore:libs.MouldShieldCore,MOULDSHIELD_CONFIG:{mode:'live',apiBaseUrl:'/api',endpoints:{},timeZone:'Europe/London'}},document:{getElementById:node},Date,console});
 const end=source.indexOf("document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener");
 vm.runInContext(source.slice(0,end)+';globalThis.testing={state,renderModeUI,updateAge};',context);
 return {node,api:context.testing};}
test('live mode removes the large banner, places source copy by the timestamp, and reveals the discreet footer action',()=>{
 const a=load();a.api.state.latest={timestamp:new Date().toISOString()};a.api.updateAge();
 assert.equal(a.node('mode-banner').hidden,true);assert.equal(a.node('live-reading-label').hidden,false);assert.equal(a.node('live-reading-label').textContent,'Live readings from your sensor');assert.equal(a.node('toggle-mode').textContent,'See example data');assert.equal(a.node('toggle-mode').hidden,false);assert.match(a.node('updated').textContent,/Reading at/);
});
test('demo mode keeps a clear banner and hides the live caption and footer example action',()=>{
 const a=load();a.api.state.mode='demo';a.api.renderModeUI();assert.equal(a.node('mode-banner').hidden,false);assert.match(a.node('mode-description').textContent,/not real sensor data/);assert.equal(a.node('live-reading-label').hidden,true);assert.equal(a.node('toggle-mode').hidden,true);
});
test('switching repeatedly between live and demo restores the right disclosure',()=>{
 const a=load();for(const mode of ['demo','live','demo','live']){a.api.state.mode=mode;a.api.renderModeUI();assert.equal(a.node('mode-banner').hidden,mode==='live');assert.equal(a.node('toggle-mode').hidden,mode==='demo');}
});
test('missing and stale readings do not claim to be current live readings',()=>{
 const a=load();a.api.updateAge();assert.equal(a.node('live-reading-label').textContent,'Waiting for your sensor');a.api.state.latest={timestamp:new Date(Date.now()-180000).toISOString()};a.api.updateAge();assert.equal(a.node('live-reading-label').textContent,'Sensor reading is out of date');
});
test('example action is in the footer, connect-to-live action is in the banner, and source caption is beside the time',()=>{
 const html=fs.readFileSync(path.join(root,'index.html'),'utf8');assert.equal((html.match(/id="toggle-mode"/g)||[]).length,1);assert.match(html,/<footer>[\s\S]*id="toggle-mode"[\s\S]*<\/footer>/);assert.match(html,/id="mode-banner"[\s\S]*id="connect-live"/);assert.match(html,/id="updated"[^>]*>[^<]*<\/span><span id="live-reading-label"/);assert.match(source,/\$\('connect-live'\)\.addEventListener\('click',switchDataMode\)/);assert.match(source,/\$\('toggle-mode'\)\.addEventListener\('click',switchDataMode\)/);
});
test('new copy translates EN to RO and back without changing the data source',()=>{
 const context=vm.createContext({module:{exports:{}}});vm.runInContext(fs.readFileSync(path.join(root,'i18n.js'),'utf8'),context);const L=context.module.exports.createI18n();L.setLanguage('ro');assert.equal(L.text('Live readings from your sensor'),'Citiri în timp real de la senzorul tău');assert.equal(L.text('See example data'),'Vezi date de exemplu');assert.match(L.text('Sample data — these are example readings, not real sensor data.'),/nu citiri reale/);L.setLanguage('en');assert.equal(L.text('See example data'),'See example data');
});
