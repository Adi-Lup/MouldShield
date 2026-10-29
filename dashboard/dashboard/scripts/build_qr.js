'use strict';
const fs=require('fs'),path=require('path');
const qrFactory=require('../vendor/qrcode.js');
const url='https://d15ad8kcnyn7ke.cloudfront.net/';
const logo=fs.readFileSync(path.join(__dirname,'../assets/logo-by-the-sharks.svg'),'utf8');
const qr=qrFactory(6,'H');qr.addData(url);qr.make();
const n=qr.getModuleCount(),margin=4,size=n+margin*2;
const navy='#13294B',blue='#2878D6';
const eyes=[[0,0],[n-7,0],[0,n-7]];
const inEye=(x,y)=>eyes.some(([ex,ey])=>x>=ex&&x<ex+7&&y>=ey&&y<ey+7);
let dots='';
for(let y=0;y<n;y++)for(let x=0;x<n;x++){
  if(qr.isDark(y,x)&&!inEye(x,y))dots+=`<rect x="${x+margin+.05}" y="${y+margin+.05}" width=".9" height=".9" rx=".22"/>`;
}
const finders=eyes.map(([x,y])=>`<g transform="translate(${x+margin} ${y+margin})"><rect width="7" height="7" rx="2.05" fill="${navy}"/><rect x="1" y="1" width="5" height="5" rx="1.1" fill="white"/><rect x="2" y="2" width="3" height="3" rx=".92" fill="${blue}"/></g>`).join('');
// Logo and white plate cover 7.92% of the data square, below the 20% area limit.
const plateW=n*.44,plateH=n*.18,logoW=n*.40,logoH=logoW*200/660;
const svg=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" role="img" aria-labelledby="qr-title"><title id="qr-title">Scan to open MouldShield live sensor readings</title><rect width="${size}" height="${size}" fill="white"/><g fill="${navy}">${dots}</g>${finders}<rect x="${(size-plateW)/2}" y="${(size-plateH)/2}" width="${plateW}" height="${plateH}" rx=".5" fill="white"/><svg x="${(size-logoW)/2}" y="${(size-logoH)/2}" width="${logoW}" height="${logoH}" viewBox="0 0 660 200">${logo.replace(/^<svg[^>]*>/,'').replace(/<\/svg>\s*$/,'')}</svg></svg>`;
const page=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>MouldShield · Live QR code</title><style>*{box-sizing:border-box}body{margin:0;background:#f3f6f2;color:#183425;font:18px/1.5 system-ui,-apple-system,Segoe UI,sans-serif;min-height:100svh;display:grid;place-items:center;padding:20px}main{width:min(700px,100%);background:white;padding:clamp(20px,4vw,40px);border:1px solid #aab8ab;border-radius:18px;text-align:center}.brand{width:min(330px,85%);height:auto;margin-bottom:20px}h1{font-size:clamp(25px,4vw,34px);line-height:1.2;margin:0 0 12px}.qr{width:min(440px,100%);margin:20px auto}.qr svg{display:block;width:100%;height:auto}.address{display:block;overflow-wrap:anywhere;color:#123f76;font-size:16px}.button{display:inline-block;padding:13px 22px;border-radius:8px;background:#234732;color:white;text-decoration:none;font-weight:700;min-height:48px;margin-top:20px}a:focus-visible{outline:3px solid #1457bc;outline-offset:5px}.note{color:#3c5142;font-size:16px;margin-bottom:0}@media print{body{padding:0;background:white}main{border:0}.button{display:none}}</style></head><body><main><img class="brand" src="data:image/svg+xml;base64,${Buffer.from(logo).toString('base64')}" width="660" height="200" alt="MouldShield by THE SHARKS"><h1>Scan for live sensor readings</h1><p>Open your phone camera and scan the code.</p><div class="qr">${svg}</div><a class="address" href="${url}">${url}</a><a class="button" href="https://d15ad8kcnyn7ke.cloudfront.net/index.html#overview">Open main dashboard</a><p class="note">THE SHARKS · T19 · Live readings, updated every 15 seconds.</p></main></body></html>`;
const target=path.join(__dirname,'../MouldShield_QR.html');fs.writeFileSync(target,page);
fs.writeFileSync(path.join(__dirname,'../MouldShield_QR.svg'),svg);
console.log('QR:',url,'H;',n,'modules;',((plateW*plateH/(n*n))*100).toFixed(1)+'% white plate including logo');
