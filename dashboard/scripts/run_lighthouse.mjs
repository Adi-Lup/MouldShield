/** Optional T22 audit. Requires Node.js, Lighthouse and a local Chrome installation. */
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {spawn} from 'node:child_process';
import readline from 'node:readline';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2);
function option(name,otherwise){const i=args.indexOf(name);return i<0?otherwise:args[i+1];}
const toolsRoot=option('--tools-root',root);
const require=createRequire(path.join(toolsRoot,'package.json'));
let lighthouse, chromeLauncher;
try{
  lighthouse=(await import(pathToFileURL(require.resolve('lighthouse')).href)).default;
  chromeLauncher=await import(pathToFileURL(require.resolve('chrome-launcher')).href);
}catch{
  console.error('Install the optional audit tool in this project: npm install --no-save lighthouse@13.5.0');
  process.exit(1);
}
const out=path.join(root,'docs','testing','lighthouse');
fs.mkdirSync(out,{recursive:true});
const python=option('--python',process.platform==='win32'?'py':'python3');
const child=spawn(python,[path.join(root,'run.py'),'--port','8765','--no-browser'],{cwd:root,stdio:['ignore','pipe','pipe']});
let chrome;
let summary=[];
try{
  const base=await new Promise((resolve,reject)=>{
    const timer=setTimeout(()=>reject(Error('Audit server did not become ready')),15000);
    const lines=readline.createInterface({input:child.stdout});
    lines.on('line',line=>{if(line.startsWith('Open your dashboard: ')){clearTimeout(timer);resolve(line.slice('Open your dashboard: '.length));}});
    child.once('error',error=>{clearTimeout(timer);reject(error);});
    child.once('exit',code=>{clearTimeout(timer);reject(Error('Audit server stopped with code '+code));});
  });
  const chromePath=option('--chrome-path',undefined);
  const chromeFlags=['--headless','--disable-gpu','--disable-dev-shm-usage'];
  if(process.getuid?.()===0)chromeFlags.push('--no-sandbox');
  chrome=await chromeLauncher.launch({chromePath,chromeFlags,logLevel:'error'});
  for(const language of ['en','ro']){
  for(const profile of ['desktop','mobile']){
    for(const view of ['overview','readings','report']){
      const flags={port:chrome.port,onlyCategories:['accessibility'],output:['html','json'],logLevel:'error',throttlingMethod:'provided',formFactor:profile==='desktop'?'desktop':'mobile',screenEmulation:{mobile:profile==='mobile',width:profile==='desktop'?1440:390,height:profile==='desktop'?1000:844,deviceScaleFactor:1,disabled:false}};
      if(profile==='desktop')flags.emulatedUserAgent=false;
      const result=await lighthouse(base+'?lang='+language+'#'+view,flags);
      if(!result||result.lhr.runtimeError)throw Error(result?.lhr.runtimeError?.message||'No audit report returned');
      const stem=path.join(out,language+'-'+profile+'-'+view);
      fs.writeFileSync(stem+'.report.html',result.report[0]);
      fs.writeFileSync(stem+'.report.json',result.report[1]);
      const failures=Object.values(result.lhr.audits).filter(a=>a.score!==null&&a.score<1&&a.scoreDisplayMode!=='manual').map(a=>({id:a.id,title:a.title,score:a.score}));
      const entry={language,profile,view,score:Math.round(result.lhr.categories.accessibility.score*100),failures,lighthouseVersion:result.lhr.lighthouseVersion,userAgent:result.lhr.environment.hostUserAgent,viewport:flags.screenEmulation};
      summary.push(entry);
      fs.writeFileSync(path.join(out,'summary.json'),JSON.stringify({runAt:new Date().toISOString(),scope:'Three dashboard views in English and Romanian, at desktop and mobile sizes, using sample data. Automated accessibility, not WCAG certification or live API testing.',results:summary},null,2));
      console.log(language+' '+profile+' '+view+': '+entry.score+'/100; '+failures.length+' failed automated audits',JSON.stringify(failures));
    }
  }
  }
}finally{
  if(chrome)await chrome.kill();
  child.kill();
}
if(summary.some(item=>item.failures.length))process.exitCode=1;
