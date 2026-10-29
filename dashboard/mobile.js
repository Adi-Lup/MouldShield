/* T19 phone page: display only; uses the team's existing reading and verify APIs. */
(function(){
'use strict';
const C=window.MouldShieldCore,P=window.MouldShieldPhone,cfg=window.MOULDSHIELD_CONFIG;
const $=id=>document.getElementById(id),params=new URLSearchParams(location.search);
const safeStore={get(k){try{return localStorage.getItem(k);}catch(e){return null;}},set(k,v){try{localStorage.setItem(k,v);}catch(e){}}};
let lang=P.language(params.get('lang')||safeStore.get('mouldshield-ui-language-v1'));
let mode='live'; // This published phone page always shows real API data.
let reading=null,verification=null,failed=false,pending=false,generation=0,controllers=[],lastAnnouncement='';
const words={en:{skip:'Skip to readings',language:'Language',temperature:'Temperature',humidity:'Relative humidity',refresh:'Refresh now',refreshing:'Refreshing…',dashboard:'Open main dashboard',footnote:'Updates every 15 seconds. One reading does not confirm mould.',low:'LOW RISK',moderate:'MODERATE RISK',high:'HIGH RISK',unknown:'Waiting for readings',stale:'Reading out of date',liveRoom:'Sensor readings',demoRoom:'Living room',sample:'Sample readings · No real data verification',live:'Live reading · Refreshes every 15 seconds',verified:'✓ Data verified',tampered:'! Tampered',neutral:'Not checked',empty:'No data to verify',unavailable:'Verification unavailable',updated:'Updated',ago:'seconds ago',waiting:'Waiting for the sensor',error:'Cannot load a current reading. Check the backend and your connection, then refresh.',demoMode:'Use sample data',liveMode:'Use live data',file:'Live data needs the local server or a hosted page. Open this project using START_PHONE_DEMO.bat.',staleNote:'The last sensor reading is over two minutes old. Check the device.',future:'The sensor timestamp is invalid. Check its clock.'},ro:{skip:'Sari la valori',language:'Limbă',temperature:'Temperatură',humidity:'Umiditate relativă',refresh:'Actualizează',refreshing:'Se actualizează…',dashboard:'Deschide tabloul de bord',footnote:'Actualizare la fiecare 15 secunde. O singură citire nu confirmă mucegaiul.',low:'RISC SCĂZUT',moderate:'RISC MODERAT',high:'RISC RIDICAT',unknown:'Se așteaptă date',stale:'Date neactualizate',liveRoom:'Date de la senzor',demoRoom:'Camera de zi',sample:'Valori demonstrative · Datele nu sunt verificate',live:'Citire în timp real · Actualizare la 15 secunde',verified:'✓ Date verificate',tampered:'! Date modificate',neutral:'Neverificat',empty:'Nu există date de verificat',unavailable:'Verificare indisponibilă',updated:'Actualizat acum',ago:'secunde',waiting:'Se așteaptă senzorul',error:'Nu se poate încărca o citire actuală. Verifică serverul și conexiunea, apoi actualizează.',demoMode:'Valori demonstrative',liveMode:'Date în timp real',file:'Datele în timp real necesită serverul local sau o pagină găzduită. Deschide proiectul prin START_PHONE_DEMO.bat.',staleNote:'Ultima citire este mai veche de două minute. Verifică dispozitivul.',future:'Ora senzorului este incorectă. Verifică ceasul acestuia.'}};
const t=key=>words[lang][key]||words.en[key];
function render(){
 document.documentElement.lang=lang;$('phone-language').value=lang;
 document.querySelectorAll('[data-t]').forEach(el=>{el.textContent=t(el.dataset.t);});
 const fresh=P.freshness(reading),level=reading&&!failed&&fresh==='current'?C.statusFor(reading.humidity_pct):'unknown';
 $('room-name').textContent=mode==='demo'?({en:{living:'Living room',bedroom:'Bedroom',kitchen:'Kitchen'},ro:{living:'Camera de zi',bedroom:'Dormitor',kitchen:'Bucătărie'}}[lang][params.get('room')]||t('demoRoom')):t('liveRoom');$('device-name').textContent=mode==='live'&&reading?reading.device_id:'';
 $('phone-risk').dataset.level=level;$('risk-icon').textContent={low:'✓',moderate:'!',high:'!',unknown:'?'}[level];
 $('risk-name').textContent=t(level==='unknown'&&fresh==='stale'&&!failed?'stale':level);
 $('phone-temperature').textContent=reading?reading.temperature_c.toFixed(1):'—';$('phone-humidity').textContent=C.humidity(reading?.humidity_pct);
 const age=P.ageSeconds(reading);$('phone-updated').textContent=age!==null?t('updated')+' '+Math.max(0,age)+' '+t('ago'):t('waiting');
 const integrity=mode==='live'&&!failed?verification:null;
 $('phone-integrity').dataset.state=integrity?.state||'neutral';
 $('phone-integrity').textContent=t(integrity?.state==='verified'?'verified':integrity?.state==='tampered'?'tampered':integrity?.checked===0?'empty':mode==='live'?'unavailable':'neutral');
 $('phone-notice').textContent=t(mode==='demo'?'sample':'live');
 const error=failed?t('error'):mode==='live'&&reading&&fresh==='stale'?t('staleNote'):reading&&fresh==='missing'?t('future'):'';
 $('phone-error').hidden=!error;$('phone-error').textContent=error;
 $('phone-refresh').disabled=pending;$('phone-refresh').textContent=t(pending?'refreshing':'refresh');
 $('phone-mode').textContent=t(mode==='demo'?'liveMode':'demoMode');
 $('phone-mode').hidden=true;
 const message=t(level)+' · '+(mode==='demo'?t('sample'):error);
 if(message!==lastAnnouncement){$('phone-announcement').textContent=message;lastAnnouncement=message;}
 document.querySelectorAll('.dashboard-link,.phone-header>a').forEach(a=>{if(!window.MOULDSHIELD_STANDALONE)a.href='index.html?mode='+mode+'&lang='+lang+'&room='+(['living','bedroom','kitchen'].includes(params.get('room'))?params.get('room'):'living')+'&scenario='+(['low','moderate','high'].includes(params.get('scenario'))?params.get('scenario'):'moderate')+'#overview';});
}
async function json(path){if(!path)throw Error('Missing endpoint');const controller=new AbortController();controllers.push(controller);const timeout=setTimeout(()=>controller.abort(),cfg.requestTimeoutMs||8000);try{const r=await fetch(cfg.apiBaseUrl.replace(/\/$/,'')+path,{headers:{Accept:'application/json'},signal:controller.signal,cache:'no-store'});if(!r.ok)throw Error('HTTP '+r.status);return await r.json();}finally{clearTimeout(timeout);}}
async function refresh(){
 const own=++generation;controllers.forEach(c=>c.abort());controllers=[];pending=true;render();
 if(mode==='demo'){
 const samples=cfg.demoReadings||{low:{temperature_c:20.1,humidity_pct:54.5},moderate:{temperature_c:20.1,humidity_pct:68.4},high:{temperature_c:21.4,humidity_pct:78.2}};
 const example=samples[params.get('scenario')]||samples.moderate,offset={living:0,bedroom:-.8,kitchen:1.1}[params.get('room')]||0;
 reading=C.normalizeReading({device_id:'demo',timestamp:new Date().toISOString(),temperature_c:example.temperature_c+offset,humidity_pct:example.humidity_pct});verification=null;failed=false;pending=false;render();return;
 }
 const results=await Promise.allSettled([json(cfg.endpoints.latest).then(C.normalizeReading),json(cfg.endpoints.verify).then(C.normalizeVerify)]);
 if(own!==generation)return;
 if(results[0].status==='fulfilled'){reading=results[0].value;failed=false;verification=results[1].status==='fulfilled'?results[1].value:null;}else{reading=null;verification=null;failed=true;}
 pending=false;render();
}
$('phone-language').addEventListener('change',e=>{lang=P.language(e.target.value);safeStore.set('mouldshield-ui-language-v1',lang);const u=new URL(location.href);u.searchParams.set('lang',lang);history.replaceState(null,'',u);render();});
$('phone-refresh').addEventListener('click',refresh);
$('phone-mode').addEventListener('click',()=>{if(location.protocol==='file:'){return;}mode='live';reading=null;verification=null;failed=false;const u=new URL(location.href);u.searchParams.set('mode',mode);history.replaceState(null,'',u);refresh();});
window.addEventListener('online',()=>{if(mode==='live')refresh();});
window.addEventListener('offline',()=>{if(mode==='live'){generation++;controllers.forEach(c=>c.abort());pending=false;failed=true;verification=null;reading=null;render();}});
setInterval(refresh,cfg.refreshIntervalMs||15000);setInterval(render,1000);refresh();
})();
