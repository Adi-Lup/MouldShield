'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
const root=path.join(__dirname,'..');
const mobile=fs.readFileSync(path.join(root,'mobile.html'),'utf8');
const scripts=[...mobile.matchAll(/<script src="([^"]+)"><\/script>/g)].map(m=>fs.readFileSync(path.join(root,m[1].split('?')[0]),'utf8'));
const library=vm.createContext({window:{},URL});scripts.slice(0,3).forEach(s=>vm.runInContext(s,library));
const C=library.MouldShieldCore;
const ok=raw=>({ok:true,json:async()=>raw});
const row={id:1,device_id:'sensor-01',timestamp:'2026-10-27T12:00:00Z',temperature_c:21.4,humidity_pct:70.4};
function dashboard(fetch){
 let now=Date.parse(row.timestamp);class Clock extends Date{static now(){return now;}}
 const context=vm.createContext({window:{MouldShieldCore:C,MOULDSHIELD_CONFIG:{mode:'live',apiBaseUrl:'/api',endpoints:{latest:'/readings/latest',history:'/readings/history',verify:'/verify',forecast:null},requestTimeoutMs:1000,timeZone:'Europe/London'}},document:{},fetch,AbortController,setTimeout,clearTimeout,Date:Clock,console,Intl});
 let source=fs.readFileSync(path.join(root,'app.js'),'utf8');
 source=source.slice(0,source.indexOf("document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener"));
 vm.runInContext(source+'\nrender=()=>{};renderChart=()=>{};renderTable=()=>{};renderForecast=()=>{};setIntegrity=()=>{};globalThis.testing={refresh,loadHistory,resetHistoryCache,state};',context);
 return {api:context.testing,advance(ms){now+=ms;}};
}
test('20 current-reading polls use one history request; a new history request starts at five minutes',async()=>{
 const counts={latest:0,history:0};const a=dashboard(async url=>{if(url.endsWith('/latest')){counts.latest++;return ok(row);}if(url.endsWith('/history')){counts.history++;return ok([row]);}return ok({status:'OK',checked:1});});
 for(let i=0;i<20;i++){await a.api.refresh();a.advance(15000);}
 assert.equal(counts.latest,20);assert.equal(counts.history,1);
 await a.api.refresh();assert.equal(counts.latest,21);assert.equal(counts.history,2);
});
test('an in-flight history request is not duplicated by another refresh',async()=>{
 let resolve,count=0;const a=dashboard(()=>{count++;return new Promise(r=>resolve=r);});
 const pending=a.api.loadHistory();a.advance(300000);await a.api.loadHistory();assert.equal(count,1);
 resolve(ok([row]));await pending;assert.equal(a.api.state.history.length,1);
});
test('history failure preserves the previous successful history and is throttled',async()=>{
 let fail=false,count=0;const a=dashboard(async()=>{count++;if(fail)throw Error('Offline');return ok([row]);});
 await a.api.loadHistory();fail=true;a.advance(300000);await a.api.loadHistory();
 assert.equal(a.api.state.history.length,1);assert.match(a.api.state.historyMessage,/previously loaded/);
 await a.api.loadHistory();assert.equal(count,2);
});
test('switching mode rejects old history and allows a new initial live load',async()=>{
 let resolve,count=0;const a=dashboard(()=>{count++;return new Promise(r=>resolve=r);});const pending=a.api.loadHistory();
 a.api.state.mode='demo';a.api.resetHistoryCache();a.api.state.history=[];resolve(ok([row]));await pending;
 assert.equal(a.api.state.history.length,0);a.api.state.mode='live';const next=a.api.loadHistory();assert.equal(count,2);resolve(ok([row]));await next;
 assert.equal(a.api.state.history.length,1);
});
function phone(query='',fail=false){const nodes=new Map(),timers=[],requests=[];
 const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',hidden:false,dataset:{},value:'',handlers:{},addEventListener(e,f){this.handlers[e]=f;}});return nodes.get(id);};
 const context=vm.createContext({window:{addEventListener(){}},document:{getElementById:node,querySelectorAll:s=>s==='.dashboard-link,.phone-header>a'?[node('main-dashboard-link')]:[],documentElement:{}},location:{search:query,href:'https://d15ad8kcnyn7ke.cloudfront.net/mobile.html'+query,protocol:'https:'},history:{replaceState(){}},localStorage:{getItem(){return null},setItem(){}},URL,URLSearchParams,AbortController,Date,console,setTimeout,clearTimeout,setInterval(fn,ms){timers.push({fn,ms});},fetch:async url=>{requests.push(url);if(fail)throw Error('Offline');return ok(url.endsWith('/verify')?{status:'OK',checked:1}:{...row,timestamp:new Date().toISOString()});}});
 context.addEventListener=()=>{};context.window=context;
 scripts.forEach(s=>vm.runInContext(s,context));return {node,timers,requests};}
const flush=()=>new Promise(r=>setImmediate(r));
test('plain mobile.html defaults to live, shows rounded humidity and uses raw humidity for risk',async()=>{
 const a=phone();await flush();assert.deepEqual(a.requests,['/api/readings/latest','/api/verify']);assert.equal(a.node('phone-humidity').textContent,'70');assert.equal(a.node('phone-risk').dataset.level,'high');assert.equal(a.node('phone-mode').hidden,true);assert.ok(a.timers.some(t=>t.ms===15000));
});
test('a stale demo query cannot turn the published mobile page into sample mode',async()=>{
 const a=phone('?mode=demo');await flush();assert.equal(a.requests.length,2);assert.match(a.node('phone-notice').textContent,/Live/);assert.equal(a.node('phone-humidity').textContent,'70');
});
test('offline mobile page never substitutes demo readings',async()=>{
 const a=phone('',true);await flush();assert.equal(a.node('phone-temperature').textContent,'—');assert.equal(a.node('phone-risk').dataset.level,'unknown');assert.equal(a.node('phone-integrity').dataset.state,'neutral');
});
test('QR file has exact production link, no demo/local address and no external assets',()=>{
 const qr=fs.readFileSync(path.join(root,'MouldShield_QR.html'),'utf8');assert.match(qr,/https:\/\/d15ad8kcnyn7ke\.cloudfront\.net\//);assert.doesNotMatch(qr,/mode=demo|terminal\.local|192\.168\.|<script[^>]*src=|<link[^>]*href=/);assert.equal(scripts.length,4);
});
