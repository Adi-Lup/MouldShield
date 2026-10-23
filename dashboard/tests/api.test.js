'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm'),fs=require('node:fs');
const C=require('../core.js');
function load(fetch){const nodes=new Map();const node=id=>{if(!nodes.has(id))nodes.set(id,{textContent:'',innerHTML:'',value:'en',disabled:false,lang:'',className:'',children:[],setAttribute(){},append(...parts){this.children.push(...parts);},classList:{add(){},remove(){}}});return nodes.get(id);};const document={getElementById:node,createElement:()=>({setAttribute(){},textContent:''}),createTextNode:text=>({textContent:text})};const context=vm.createContext({window:{MouldShieldCore:C,MOULDSHIELD_CONFIG:{mode:'live',apiBaseUrl:'http://api.example.test',endpoints:{verify:'/verify',report:'/report'},requestTimeoutMs:1000,reportLanguageField:'language',timeZone:'Europe/London'}},document,fetch,AbortController,setTimeout,clearTimeout,Date,console,Intl,localStorage:{getItem(){return null},setItem(){},removeItem(){}}});const source=fs.readFileSync(__dirname+'/../app.js','utf8');const marker="document.querySelectorAll('[data-view]').forEach(b=>b.addEventListener";vm.runInContext(source.slice(0,source.indexOf(marker))+';globalThis.apiTest={api,verify,generateExplanation,state};',context);return {api:context.apiTest,node};}
const response=raw=>({ok:true,json:async()=>raw});
test('GET /verify is called exactly and OK makes Data verified',async()=>{let request;const {api,node}=load(async(url,opts)=>{request={url,opts};return response({status:'OK',checked:131});});await api.verify();assert.equal(request.url,'http://api.example.test/verify');assert.equal(request.opts.method,'GET');assert.equal(api.state.verification.state,'verified');assert.equal(api.state.verification.label,'Data verified');assert.equal(node('integrity-badge').className,'integrity-badge verified');});
test('Tampered is red and network/server failures become neutral',async()=>{let fail=false;const {api,node}=load(async()=>{if(fail)throw Error('Offline');return response({status:'Tampered',first_bad_id:12,checked:11});});await api.verify();assert.equal(api.state.verification.label,'Tampered');assert.equal(node('integrity-badge').className,'integrity-badge tampered');fail=true;await api.verify();assert.equal(api.state.verification.state,'neutral');assert.equal(api.state.verification.label,'Verification unavailable');});
test('T13 POST sends the selected tenant language and exact humidity',async()=>{for(const language of ['en','ro','pl']){let request;const {api,node}=load(async(url,opts)=>{request={url,opts};return response({explanation:'Translated explanation',letter:'Dear landlord'});});api.state.report={id:9,source:'live',device_id:'mouldshield-01',timestamp:'2026-10-23T12:00:00Z',temperature_c:20.1,humidity_pct:68.4};node('report-language').value=language;await api.generateExplanation();assert.equal(request.url,'http://api.example.test/report');assert.equal(request.opts.method,'POST');const body=JSON.parse(request.opts.body);assert.equal(body.language,language);assert.equal(body.humidity_pct,68.4);assert.equal(node('report-explanation').lang,language);assert.equal(node('report-explanation').textContent,'Translated explanation');}});
test('rapid language changes do not allow an older response to overwrite the latest',async()=>{const waits=[];const {api,node}=load(()=>new Promise(resolve=>waits.push(resolve)));api.state.report={source:'live',humidity_pct:68.4,temperature_c:20.1,timestamp:'2026-10-23T12:00:00Z',device_id:'device'};node('report-language').value='ro';const first=api.generateExplanation();node('report-language').value='pl';const second=api.generateExplanation();waits[1](response({explanation:'Polski result'}));await second;waits[0](response({explanation:'Romanian result'}));await first;assert.equal(node('report-explanation').textContent,'Polski result');assert.equal(node('report-explanation').lang,'pl');});

test('sample explanations match low and high risk in every supported language',async()=>{
  const {api,node}=load(async()=>{throw Error('Demo must not fetch');});
  for(const language of ['en','ro','pl']){
    node('report-language').value=language;
    api.state.report={source:'demo',humidity_pct:54.5};
    await api.generateExplanation();
    const low=node('report-explanation').textContent;
    api.state.report={source:'demo',humidity_pct:78.2};
    await api.generateExplanation();
    const high=node('report-explanation').textContent;
    assert.notEqual(low,high);
    assert.equal(node('report-explanation').lang,language);
    if(language==='en'){
      assert.match(low,/lower project warning band/);
      assert.match(high,/high project warning band/);
    }
  }
});

test('language changes clear the old explanation and English API errors keep English language markup',async()=>{
  const waits=[];
  const {api,node}=load(()=>new Promise((resolve,reject)=>waits.push({resolve,reject})));
  api.state.report={source:'live',humidity_pct:68.4,temperature_c:20.1,timestamp:'2026-10-23T12:00:00Z',device_id:'device'};
  node('report-explanation').textContent='Previous English explanation';
  node('report-language').value='ro';
  const pending=api.generateExplanation();
  assert.equal(node('report-explanation').textContent,'');
  waits[0].reject(Error('Service unavailable'));
  await pending;
  assert.match(node('report-explanation').textContent,/unavailable/);
  assert.equal(node('report-explanation').lang,'en');
});
