/* T20: local PDF creation. Text is supplied by the report snapshot, never invented here. */
(function(root){
'use strict';
const languages={en:'English',ro:'Română',pl:'Polski'};
function model(input){
 if(!input||!['live','demo'].includes(input.source)||!Number.isFinite(input.temperature_c)||!Number.isFinite(input.humidity_pct)||input.humidity_pct<0||input.humidity_pct>100||!Number.isFinite(Date.parse(input.timestamp)))throw Error('A valid reading is needed before downloading a report.');
 if(!languages[input.explanationLanguage]||typeof input.explanation!=='string'||!input.explanation.trim())throw Error('Generate the explanation in your chosen language first.');
 if(typeof input.letter!=='string'||!input.letter.trim())throw Error('Add the landlord letter before downloading.');
 const demo=input.source==='demo';
 const verification=demo?{state:'neutral',label:'Not checked - example data'}:input.verification&&['verified','tampered','neutral'].includes(input.verification.state)?input.verification:{state:'neutral',label:'Verification unavailable'};
 return {...input,verification,photos:Array.isArray(input.photos)?input.photos:[],level:input.humidity_pct>70?'HIGH':input.humidity_pct>60?'MODERATE':'LOW'};
}
function create(input){
 const r=model(input),Ctor=root.jspdf?.jsPDF,fonts=root.MouldShieldPdfFonts;
 if(!Ctor||!fonts)throw Error('The PDF files did not load. Reload the page and try again.');
 const doc=new Ctor({unit:'mm',format:'a4',compress:true,putOnlyUsedFonts:true});
 for(const style of ['normal','bold']){doc.addFileToVFS('DejaVu-'+style+'.ttf',fonts[style]);doc.addFont('DejaVu-'+style+'.ttf','DejaVu',style);}
 doc.setProperties({title:'MouldShield tenant report',subject:'Humidity readings, explanation and draft landlord letter',author:'THE SHARKS',creator:'MouldShield T20'});
 const left=17,width=176,bottom=273;let y=43;
 const font=(size=10.5,bold=false)=>{doc.setFont('DejaVu',bold?'bold':'normal');doc.setFontSize(size);doc.setTextColor(25,45,35);};
 function header(){
  if(root.MouldShieldPdfLogo)doc.addImage(root.MouldShieldPdfLogo,'PNG',left,10,56,17);
  else{font(19,true);doc.text('MouldShield',left,21);}
  font(8);doc.text('THE SHARKS | Tenant report',193,17,{align:'right'});
  const example=r.source==='demo';doc.setFillColor(...(example?[255,239,191]:[232,241,234]));doc.rect(left,30,width,8,'F');font(9,true);doc.text(example?'EXAMPLE DATA - NOT REAL SENSOR EVIDENCE':'LIVE SENSOR REPORT',left+3,35.5);y=46;
 }
 function ensure(height){if(y+height>bottom){doc.addPage();header();}}
 function paragraph(value,size=10.5,bold=false){
  font(size,bold);
  const lines=doc.splitTextToSize(String(value).replace(/\r\n?/g,'\n'),width),step=size*.3528*1.45;
  for(const line of lines){ensure(step);font(size,bold);if(line)doc.text(line,left,y);y+=step;}
  y+=3;
 }
 function section(title){ensure(20);y+=4;paragraph(title,12,true);}
 header();paragraph('Your home report',19,true);
 paragraph('Reading time (UTC): '+new Date(r.timestamp).toISOString());
 paragraph('Device: '+String(r.device_id||'Not supplied'));
 paragraph('Temperature: '+r.temperature_c.toFixed(1)+' °C');
 paragraph('Humidity: '+Math.round(r.humidity_pct)+'% RH (original reading: '+String(r.humidity_pct)+'% RH)');
 const colour={LOW:[23,75,46],MODERATE:[76,54,0],HIGH:[118,24,33]}[r.level];
 font(12,true);doc.setTextColor(...colour);doc.text(r.level+' RISK',left,y);y+=9;
 section('Data integrity');
 paragraph(r.verification.label||'Verification unavailable');
 if(r.verification.detail)paragraph(r.verification.detail,9);
 if(r.verificationCheckedAt)paragraph('Check time (UTC): '+r.verificationCheckedAt,9);
 if(r.verification.state==='tampered')paragraph('WARNING: the data integrity check failed. These records must not be described as verified.',10,true);
 section('Explanation ('+languages[r.explanationLanguage]+')');paragraph(r.explanation);
 if(r.explanationSource==='fixed')paragraph('The service supplied its standard explanation because a generated explanation was unavailable.',8.5);
 paragraph('The draft letter starts on the next page.',9);doc.addPage();header();section('Draft letter to your landlord');paragraph(r.letter);
 for(const [index,photo] of r.photos.entries()){
  if(!photo.dataUrl||!/^data:image\/(png|jpeg);base64,/.test(photo.dataUrl))throw Error('A selected evidence photo could not be included.');
  section('Photo evidence '+(index+1));
  const props=doc.getImageProperties(photo.dataUrl),h=Math.min(95,width*props.height/props.width),w=h*props.width/props.height;ensure(h+6);doc.addImage(photo.dataUrl,undefined,left,y,w,h);y+=h+5;
  if(photo.description)paragraph(photo.description,9.5);
  if(photo.details)paragraph(photo.details,8.5);
 }
 section('Before sharing');paragraph('Review this draft and replace any placeholders with accurate details. A single humidity reading does not confirm mould or replace a property inspection. The report is not an official HHSRS assessment. Nothing is sent to your landlord automatically.',9);
 const pages=doc.getNumberOfPages();for(let i=1;i<=pages;i++){doc.setPage(i);doc.setDrawColor(165,180,170);doc.line(left,280,193,280);font(8);doc.text(r.source==='demo'?'EXAMPLE DATA - NOT REAL EVIDENCE':'MouldShield | Review before sharing',left,286);doc.text(i+' / '+pages,193,286,{align:'right'});}
 return doc;
}
function filename(input){return 'MouldShield_Report_'+new Date(input.timestamp).toISOString().slice(0,10)+'_'+input.explanationLanguage+'.pdf';}
root.MouldShieldPDF={model,create,filename};
})(typeof window!=='undefined'?window:globalThis);
