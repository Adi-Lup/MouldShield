'use strict';
const test=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.join(__dirname,'..'),window={jspdf:require('../vendor/jspdf.umd.min.js')};
const context=vm.createContext({window,console});vm.runInContext(fs.readFileSync(path.join(root,'pdf-fonts.js'),'utf8'),context);vm.runInContext(fs.readFileSync(path.join(root,'pdf-report.js'),'utf8'),context);
const P=window.MouldShieldPDF;
const report=(extra={})=>({id:1,source:'demo',timestamp:'2026-10-28T12:00:00Z',device_id:'test-device',temperature_c:20.1,humidity_pct:68.4,explanation:'Example reading; one reading does not confirm mould.',explanationLanguage:'en',letter:'Dear landlord,\n\nPlease inspect [room].\n\n[Your name]',...extra});
test('PDF model requires real reading fields, explanation, language and a letter',()=>{
 for(const x of [null,report({humidity_pct:101}),report({timestamp:'bad'}),report({explanation:''}),report({explanationLanguage:'xx'}),report({letter:''})])assert.throws(()=>P.model(x));
});
test('PDF risk uses original precision and does not mutate the reading',()=>{const r=report({humidity_pct:70.4});assert.equal(P.model(r).level,'HIGH');assert.equal(r.humidity_pct,70.4);});
test('sample reports cannot turn a passed verification into real evidence',()=>{const r=P.model(report({verification:{state:'verified',label:'Data verified'}}));assert.equal(r.verification.state,'neutral');assert.match(r.verification.label,/example data/);});
test('tampered evidence retains a failed integrity state in live reports',()=>{const r=P.model(report({source:'live',verification:{state:'tampered',label:'Tampered'}}));assert.equal(r.verification.state,'tampered');});
test('PDF files render all supported explanation languages using embedded Unicode fonts',()=>{for(const [lang,text] of [['en','Example humidity reading.'],['ro','Umiditate ridicată. Verifică încăperea și păstrează citirile.'],['pl','Wilgotność jest podwyższona. Sprawdź ściany.']]){const doc=P.create(report({explanationLanguage:lang,explanation:text}));const data=Buffer.from(doc.output('arraybuffer'));assert.equal(data.subarray(0,5).toString(),'%PDF-');assert.ok(data.length>20000);assert.ok(doc.getNumberOfPages()>=1);}});
test('long letters paginate instead of being truncated',()=>{const doc=P.create(report({letter:('A test line describing the tenant observations.\n').repeat(180)}));assert.ok(doc.getNumberOfPages()>=4);});
test('PDF filename records the reading date and selected explanation language',()=>{assert.equal(P.filename(report({explanationLanguage:'ro'})),'MouldShield_Report_2026-10-28_ro.pdf');});
test('unavailable or unsupported selected photo evidence blocks a misleading export',()=>{assert.throws(()=>P.create(report({photos:[{dataUrl:'https://outside.test/photo.jpg'}]})),/photo/);});
test('selected clean PNG evidence is embedded in the PDF',()=>{const base=P.create(report()).getNumberOfPages();const doc=P.create(report({photos:[{dataUrl:window.MouldShieldPdfLogo,description:'T22 test image - team logo, not damp evidence.',details:'Synthetic fixture only.'}]}));assert.ok(doc.getNumberOfPages()>=base);assert.match(doc.output(),/\/Subtype \/Image/);});
