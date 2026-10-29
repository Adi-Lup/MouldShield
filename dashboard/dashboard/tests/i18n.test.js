'use strict';
const test=require('node:test'),assert=require('node:assert/strict');
const {createI18n}=require('../i18n.js');
test('interface language switches between English and Romanian with English fallback',()=>{
 const i=createI18n();assert.equal(i.text('Overview'),'Overview');
 assert.equal(i.setLanguage('ro'),'ro');assert.equal(i.text('Overview'),'Prezentare generală');
 assert.equal(i.text('  A little attention\ngoes a long way. '),'  Puțină atenție face diferența. ');
 assert.equal(i.text('External service content'),'External service content');
 assert.equal(i.setLanguage('invalid'),'en');assert.equal(i.text('Overview'),'Overview');
});
test('dynamic labels translate without changing numeric readings, addresses or identifiers',()=>{
 const i=createI18n();i.setLanguage('ro');
 assert.equal(i.text('! MODERATE RISK'),'! RISC MODERAT');
 assert.equal(i.text('68.4%'),'68.4%');
 assert.equal(i.text('Light rain, 9.0 °C'),'Ploaie ușoară, 9.0 °C');
 assert.equal(i.text('131 readings checked in the whole chain.'),'131 citiri verificate în întregul lanț.');
 assert.equal(i.text('Live API mode. Source: /api'),'Mod API live. Sursa: /api');
 assert.equal(i.text('Sample at 16:10 · 9s ago'),'Exemplu la 16:10 · acum 9 s');
});
function documentFixture(nodes,attributes=[]){
 return {title:'MouldShield · Your home, in view',documentElement:{lang:'en'},body:{querySelectorAll:()=>attributes},createTreeWalker(){let i=0;return{nextNode:()=>nodes[i++]||null};}};
}
const textNode=(value,excluded=false)=>({nodeValue:value,parentElement:{closest:()=>excluded?{}:null}});
test('switching back restores English and new live labels update the translation source',()=>{
 const i=createI18n(),node=textNode('Overview'),doc=documentFixture([node]);
 i.setLanguage('ro');i.apply(doc);assert.equal(node.nodeValue,'Prezentare generală');assert.equal(doc.documentElement.lang,'ro');
 i.apply(doc);assert.equal(node.nodeValue,'Prezentare generală');
 i.setLanguage('en');i.apply(doc);assert.equal(node.nodeValue,'Overview');
 node.nodeValue='Sensor readings';i.setLanguage('ro');i.apply(doc);assert.equal(node.nodeValue,'Citiri senzor');
 i.setLanguage('en');i.apply(doc);assert.equal(node.nodeValue,'Sensor readings');
});
test('report responses and editable letter content remain unchanged while accessible names translate',()=>{
 const i=createI18n(),explanation=textNode('Translated service response',true),letter=textNode('Dear landlord, my edited draft',true);
 const values={'aria-label':'Refresh readings'},el={hasAttribute:k=>Object.hasOwn(values,k),getAttribute:k=>values[k],setAttribute:(k,v)=>values[k]=v};
 const doc=documentFixture([explanation,letter],[el]);i.setLanguage('ro');i.apply(doc);
 assert.equal(explanation.nodeValue,'Translated service response');assert.equal(letter.nodeValue,'Dear landlord, my edited draft');
 assert.equal(values['aria-label'],'Actualizează citirile');
 i.setLanguage('en');i.apply(doc);assert.equal(values['aria-label'],'Refresh readings');
});
