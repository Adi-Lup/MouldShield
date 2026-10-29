/* T19: small, testable helpers shared by the phone and QR pages. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.MouldShieldPhone=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
function language(value){return value==='ro'?'ro':'en';}
function isLoopback(host){const h=host.toLowerCase().replace(/^\[|\]$/g,'');return h==='localhost'||h.endsWith('.localhost')||h==='::1'||h.startsWith('127.')||h==='0.0.0.0'||h==='::'||h==='[::]';}
function mobileUrl(input,{lang='en',mode='live',room,scenario}={}){
 const value=String(input||'').trim();if(!value||value.length>700)throw Error('address');
 let u;try{u=new URL(value);}catch(e){throw Error('address');}
 if(!['http:','https:'].includes(u.protocol)||u.username||u.password||isLoopback(u.hostname))throw Error('address');
 if(u.pathname.endsWith('/mobile.html')){}else if(/\/[^/]+\.html$/i.test(u.pathname))u.pathname=u.pathname.replace(/[^/]+\.html$/i,'mobile.html');else u.pathname=u.pathname.replace(/\/?$/,'/')+'mobile.html';
 u.search='';u.hash='';u.searchParams.set('mode',mode==='demo'?'demo':'live');u.searchParams.set('lang',language(lang));if(['living','bedroom','kitchen'].includes(room))u.searchParams.set('room',room);if(['low','moderate','high'].includes(scenario))u.searchParams.set('scenario',scenario);return u.href;
}
function ageSeconds(reading,now=Date.now()){if(!reading)return null;return Math.floor((now-Date.parse(reading.timestamp))/1000);}
function freshness(reading,now=Date.now()){const age=ageSeconds(reading,now);if(age===null||!Number.isFinite(age)||age< -30)return 'missing';return age>120?'stale':'current';}
function svgForUrl(url,makeQr){const qr=makeQr(0,'M');qr.addData(url,'Byte');qr.make();const n=qr.getModuleCount(),q=4,size=n+q*2;let path='';for(let y=0;y<n;y++)for(let x=0;x<n;x++)if(qr.isDark(y,x))path+='M'+(x+q)+' '+(y+q)+'h1v1h-1z';return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 '+size+' '+size+'" width="360" height="360" shape-rendering="crispEdges" role="img" aria-label="MouldShield QR code"><rect width="'+size+'" height="'+size+'" fill="white"/><path d="'+path+'" fill="black"/></svg>';}
return {language,isLoopback,mobileUrl,ageSeconds,freshness,svgForUrl};
});
