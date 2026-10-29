/* EN / RO interface copy. Sensor values and editable/user-authored content are never translated. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports={createI18n:factory};else root.MouldShieldI18n=factory();})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
let locale='en';
const textRecords=new WeakMap(),attributeRecords=new WeakMap();
const ro={
'Review the letter, then download the PDF or print the report. Nothing is sent automatically.':'Verifică scrisoarea, apoi descarcă PDF-ul sau tipărește raportul. Nu se trimite nimic automat.',
'Save PDF':'Salvează PDF',
'Your PDF is ready. If saving did not start, choose Save PDF.':'PDF-ul este gata. Dacă salvarea nu a pornit, apasă Salvează PDF.',
'Download PDF':'Descarcă PDF',
'Preparing your PDF…':'Se pregătește PDF-ul…',
'PDF downloaded. Review it before sharing.':'PDF descărcat. Verifică-l înainte de a-l trimite.',
'Explore your sensor history.':'Explorează istoricul citirilor de la senzor.',
'Review the sensor summary.':'Verifică rezumatul citirilor de la senzor.',
'Open QR code':'Deschide codul QR',
'Sample data — these are example readings, not real sensor data.':'Date demonstrative — acestea sunt exemple, nu citiri reale de la senzor.',
'Live readings from your sensor':'Citiri în timp real de la senzorul tău',
'See example data':'Vezi date de exemplu',
'Connect to live readings':'Conectează citirile reale',
'Waiting for your sensor':'Se așteaptă date de la senzor',
'Sensor reading is out of date':'Citirea senzorului nu mai este actuală',
'Waiting for a reading':'Se așteaptă o citire',
'MouldShield · Your home, in view':'MouldShield · Locuința ta, la vedere',
'MouldShield - standalone preview':'MouldShield - previzualizare independentă',
'Dashboard language':'Limba interfeței',
'Skip to content':'Sari la conținut','Main navigation':'Navigare principală','My home':'Locuința mea','Tenant workspace':'Spațiul chiriașului','YOUR SPACE':'SPAȚIUL TĂU',
'Overview':'Prezentare generală','Sensor readings':'Citiri senzor','My report':'Raportul meu','A clearer picture.':'O imagine mai clară.','A more comfortable home.':'O locuință mai confortabilă.',
'Understand your readings, one day at a time.':'Înțelege valorile înregistrate, zi după zi.','Computing · Project prototype':'Informatică · Prototip de proiect',
'Starting dashboard. If this message stays, extract the entire ZIP and open START_HERE.html or START_WINDOWS.bat.':'Se încarcă panoul. Dacă mesajul rămâne, extrage întreaga arhivă ZIP și deschide START_HERE.html sau START_WINDOWS.bat.',
'Preview with sample data. Live API features are not connected.':'Previzualizare cu date demonstrative. API-ul live nu este conectat.',
'Connect to API':'Conectează API-ul','Show demo':'Arată demonstrația','Sample readings and forecast. No real data verification.':'Citiri și prognoză demonstrative. Datele reale nu sunt verificate.',
'A LITTLE KNOWLEDGE. A HEALTHIER HOME.':'INFORMAȚII CLARE. O LOCUINȚĂ MAI SĂNĂTOASĂ.',
'Your home, in view':'Locuința ta, la vedere','Clear readings. Simple signals. A little more peace of mind.':'Citiri clare. Semnale simple. Mai multă liniște.',
'Create a report':'Creează un raport','Monitoring':'Monitorizare','Living room':'Sufragerie','Bedroom':'Dormitor','Kitchen':'Bucătărie','Device':'Dispozitiv',
'Sample refreshed just now':'Exemplu actualizat acum','Refresh readings':'Actualizează citirile','CURRENT STATUS':'STAREA ACTUALĂ',
'LOW RISK':'RISC REDUS','MODERATE RISK':'RISC MODERAT','HIGH RISK':'RISC RIDICAT','NO CURRENT READING':'NICIO CITIRE ACTUALĂ',
'Low risk':'Risc redus','Moderate risk':'Risc moderat','High risk':'Risc ridicat','Low':'Redus','Moderate':'Moderat','High':'Ridicat','Sample risk status':'Nivel de risc demonstrativ',
'A little attention goes a long way.':'Puțină atenție face diferența.',
'Humidity is above the preferred range. Watch the trend and check for condensation.':'Umiditatea depășește intervalul recomandat. Urmărește evoluția și verifică dacă apare condens.',
'Humidity is within the lower warning band. Check the trend for changes.':'Umiditatea se află în intervalul cu risc redus. Urmărește evoluția valorilor.',
'Keep your good routine going':'Păstrează obiceiurile bune',
'Use extractor fans when cooking or showering and keep an eye on cold windows and walls.':'Folosește ventilația când gătești sau faci duș și verifică ferestrele și pereții reci.',
'Time to take a closer look.':'Este timpul să verifici mai atent.',
'Humidity is high. Check for damp or condensation and report persistent concerns.':'Umiditatea este ridicată. Verifică umezeala sau condensul și raportează problemele persistente.',
'Check for signs of damp':'Verifică semnele de umezeală',
'Keep a record of moisture, leaks or visible mould, and report persistent problems to your landlord.':'Notează umezeala, infiltrațiile sau mucegaiul vizibil și anunță proprietarul dacă problemele persistă.',
'Waiting for your sensor.':'Se așteaptă senzorul.',
'No valid current reading is available. A green risk status is not assumed.':'Nu există o citire actuală validă. Nu se presupune automat un risc redus.',
'Check your connection':'Verifică conexiunea',
'Make sure the sensor is switched on and connected to Wi-Fi, then refresh the page.':'Verifică dacă senzorul este pornit și conectat la Wi-Fi, apoi reîncarcă pagina.',
'The reading is out of date.':'Citirea nu mai este actuală.',
'The last reading is older than two minutes. Check the device connection.':'Ultima citire este mai veche de două minute. Verifică legătura cu dispozitivul.',
'TEMPERATURE':'TEMPERATURĂ','Temperature':'Temperatură','Latest room temperature':'Ultima temperatură din cameră','Sample sensor reading':'Citire demonstrativă','Original API reading':'Citire originală din API',
'RELATIVE HUMIDITY':'UMIDITATE RELATIVĂ','Humidity':'Umiditate','Preferred range: 40–60% RH':'Interval recomandat: 40–60% RH',
'Above the preferred range':'Peste intervalul recomandat','Within the preferred range':'În intervalul recomandat','Below the preferred range':'Sub intervalul recomandat','Waiting for data':'Se așteaptă date',
'Humidity over 24 hours':'Umiditatea în ultimele 24 de ore','Daily humidity over 7 days':'Umiditatea zilnică în ultimele 7 zile',
'Your room’s story, a reading at a time.':'Evoluția camerei tale, citire cu citire.','Chart time range':'Perioada graficului','24 h':'24 h','7 days':'7 zile',
'Preferred range':'Interval recomandat','Sample history':'Istoric demonstrativ','API history':'Istoric din API','Daily averages and hours above 70%':'Medii zilnice și ore peste 70%',
'Seven-day humidity summary; gaps are not counted as exposure.':'Rezumat pe 7 zile; perioadele fără date nu sunt numărate ca expunere.',
'Day':'Zi','Average RH':'Umiditate medie','Hours above 70%':'Ore peste 70%','Coverage':'Acoperire','average':'medie','lowest':'minim','highest':'maxim','No data':'Fără date',
'No history data available':'Nu există date istorice','Daily average humidity and hours above 70 percent':'Umiditatea medie zilnică și orele peste 70%',
'Relative humidity over the last 24 hours':'Umiditatea relativă în ultimele 24 de ore',
'Seven daily bars showing average humidity. Hours above 70 percent appear under each bar and in the accessible data table.':'Șapte bare arată umiditatea medie zilnică. Orele peste 70% apar sub fiecare bară și în tabelul accesibil.',
'Illustrative relative humidity trend over the last 24 hours':'Evoluție demonstrativă a umidității în ultimele 24 de ore',
'Illustrative history; no database values have been changed.':'Istoric demonstrativ; valorile din baza de date nu au fost modificate.',
'History is not connected. Set the agreed history endpoint in config.js.':'Istoricul nu este conectat. Configurează ruta stabilită în config.js.',
'Original-precision readings from the API.':'Citiri din API cu precizia originală.','No history readings returned.':'API-ul nu a returnat citiri istorice.',
'A small step today':'Un pas mic astăzi','Keep an eye on condensation':'Urmărește apariția condensului',
'Look for moisture on windows and cold walls. Use extractor fans when cooking or showering.':'Verifică umezeala pe ferestre și pereți reci. Folosește ventilația când gătești sau faci duș.',
'Persistent damp or visible mould should be reported to your landlord.':'Umezeala persistentă sau mucegaiul vizibil trebuie raportate proprietarului.',
'How are the colours chosen?':'Cum sunt alese culorile?','THE NEXT 24–48 HOURS':'URMĂTOARELE 24–48 DE ORE','Condensation forecast':'Prognoza condensului',
'Not connected':'Neconectat','Unavailable':'Indisponibil','Sample forecast':'Prognoză demonstrativă','Weather unavailable':'Date meteo indisponibile',
'Condensation warning not available yet.':'Avertizarea privind condensul nu este disponibilă încă.',
'Outside now':'Afară acum','Tonight’s minimum':'Minima din această noapte','Tomorrow':'Mâine',
'Forecast supplied by the project back-end, using Open-Meteo.':'Prognoză furnizată de serverul proiectului, folosind Open-Meteo.',
'No condensation or outside-temperature values are shown when the forecast is unavailable.':'Când prognoza nu este disponibilă, nu sunt afișate valori pentru condens sau temperatura exterioară.',
'Forecast unavailable: the forecast address is not set.':'Prognoza nu este disponibilă: adresa prognozei nu este setată.','Loading forecast…':'Se încarcă prognoza…',
'Sample warning: colder conditions tonight may increase condensation risk.':'Avertizare demonstrativă: vremea mai rece din această noapte poate crește riscul de condens.',
'YOUR EVIDENCE':'DOVEZILE TALE','Reading integrity':'Integritatea citirilor','Not checked':'Neverificat','Not checked · demo':'Neverificat · demonstrație',
'Data verified':'Date verificate','Tampered':'Date modificate','No data to verify':'Nu există date de verificat','Verification unavailable':'Verificare indisponibilă','Checking data…':'Se verifică datele…',
'The saved chain did not match.':'Lanțul salvat nu corespunde.','The database contains no readings.':'Baza de date nu conține citiri.',
'A green result is shown only after GET /verify confirms a non-empty chain.':'Rezultatul verde apare numai după ce GET /verify confirmă un lanț cu date.',
'Sample data is not certified. Connect to the API to call GET /verify.':'Datele demonstrative nu sunt certificate. Conectează API-ul pentru GET /verify.',
'Requesting GET /verify from the project API.':'Se solicită GET /verify de la API-ul proiectului.','Check data integrity':'Verifică integritatea datelor',
'Try the prototype':'Încearcă prototipul','Sample readings only; verification is never simulated as a real result.':'Doar citiri demonstrative; verificarea nu este prezentată ca un rezultat real.',
'THE NUMBERS BEHIND THE SIGNAL':'VALORILE DIN SPATELE SEMNALULUI','Explore the sample history for your selected room.':'Explorează istoricul demonstrativ pentru camera aleasă.',
'Export CSV':'Exportă CSV','These are sample readings, not live device data.':'Acestea sunt citiri demonstrative, nu date live de la dispozitiv.',
'Raw values retained in CSV':'Valorile exacte sunt păstrate în CSV','Time':'Ora','Status':'Stare','recent samples':'exemple recente','recent readings':'citiri recente',
'Sample readings only. CSV retains the original decimal values.':'Doar citiri demonstrative. CSV păstrează valorile zecimale originale.',
'Latest reading and configured history from the API. CSV retains the original decimal values.':'Ultima citire și istoricul configurat din API. CSV păstrează valorile zecimale originale.',
'No readings available.':'Nu există citiri disponibile.','TURN READINGS INTO A CONVERSATION':'TRANSFORMĂ CITIRILE ÎNTR-O DISCUȚIE','Your home report':'Raportul locuinței tale',
'A clear summary and a letter you can make your own.':'Un rezumat clar și o scrisoare pe care o poți adapta.','Print / save PDF':'Tipărește / salvează PDF',
'Use your browser’s print dialog to save a PDF. No letter is sent automatically.':'Folosește fereastra de tipărire pentru a salva PDF-ul. Scrisoarea nu este trimisă automat.',
'Damp & humidity summary':'Rezumat privind umezeala și umiditatea','Explanation language':'Limba explicației','English':'Engleză','Română':'Română','Polski':'Polski',
'Generate explanation':'Generează explicația','Choose the tenant’s explanation language. The interface language is selected above.':'Alege limba explicației pentru chiriaș. Limba interfeței se alege sus.',
'What the readings mean':'Ce înseamnă citirile','Letter to your landlord':'Scrisoare către proprietar',
'Edit this draft before downloading. Changes stay in this browser.':'Editează această ciornă înainte de descărcare. Modificările rămân în acest browser.',
'Reset draft':'Resetează ciorna','Draft ready to edit':'Ciorna poate fi editată','Saved draft restored from this browser':'Ciorna salvată a fost restaurată din browser','Draft reset':'Ciorna a fost resetată',
'Draft saved in this browser':'Ciorna a fost salvată în browser','Draft updated; browser storage is unavailable.':'Ciorna a fost actualizată; stocarea în browser nu este disponibilă.',
'One reading does not confirm mould or replace an inspection. Letters are drafts for review.':'O singură citire nu confirmă mucegaiul și nu înlocuiește o inspecție. Scrisorile sunt ciorne care trebuie verificate.',
'Your voice. Your report.':'Vocea ta. Raportul tău.',
'Add your address and describe what you have noticed. Keep the details accurate and review the letter before using it.':'Adaugă adresa și descrie ce ai observat. Verifică exactitatea detaliilor și citește scrisoarea înainte de folosire.',
'Check the sample summary.':'Verifică rezumatul demonstrativ.','Edit the landlord letter.':'Editează scrisoarea către proprietar.','Print or save a PDF.':'Tipărește sau salvează un PDF.',
'Only include information you are comfortable sharing.':'Include numai informațiile pe care dorești să le comunici.',
'Choose a language and generate an explanation.':'Alege o limbă și generează explicația.','No valid reading available for this report.':'Nu există o citire validă pentru acest raport.','? No reading available':'? Nu există o citire disponibilă',
'Draft letter returned by the API; review before use.':'Ciorna a fost furnizată de API; verific-o înainte de folosire.',
'Understanding your risk colour':'Ce înseamnă culoarea riscului','Close explanation':'Închide explicația',
'The warning bands use the original, unrounded relative humidity reading. Humidity is rounded only for display.':'Nivelurile de avertizare folosesc valoarea originală, nerotunjită, a umidității relative. Rotunjirea este folosită doar la afișare.',
'60% RH or below':'60% RH sau mai puțin','Above 60%, up to 70% RH':'Peste 60%, până la 70% RH','Above 70% RH':'Peste 70% RH',
'40–60% RH is the preferred indoor range used in the project research. Very dry air below 40% is outside that range, even though this mould-warning scale stays green.':'40–60% RH este intervalul interior recomandat în cercetarea proiectului. Aerul foarte uscat, sub 40%, este în afara intervalului, chiar dacă această scară de avertizare rămâne verde.',
'These are project warning bands, not an HHSRS assessment. Duration, cold surfaces and other conditions also matter. The sustained-risk rule still needs team agreement.':'Acestea sunt nivelurile de avertizare ale proiectului, nu o evaluare HHSRS. Contează și durata, suprafețele reci și alte condiții. Regula pentru risc persistent trebuie stabilită de echipă.',
'Readings exported at their original precision.':'Citirile au fost exportate cu precizia originală.',
'For live data, start START_WINDOWS.bat and use the local server address it prints.':'Pentru date live, pornește START_WINDOWS.bat și folosește adresa locală afișată.',
'Sample data':'Date demonstrative','API mode':'Mod API','Now':'Acum','No current reading':'Nu există o citire actuală','Loading sample…':'Se încarcă exemplul…',
'The current latest-reading endpoint returns one device, without room filtering.':'Ruta ultimei citiri returnează un singur dispozitiv, fără filtrare după cameră.',
'Mon':'lun.','Tue':'mar.','Wed':'mie.','Thu':'joi','Fri':'vin.','Sat':'sâm.','Sun':'dum.',
'Clear sky':'Cer senin','Mainly clear':'Predominant senin','Partly cloudy':'Parțial noros','Overcast':'Cer acoperit','Fog':'Ceață','Depositing rime fog':'Ceață cu chiciură',
'Light drizzle':'Burniță ușoară','Moderate drizzle':'Burniță moderată','Dense drizzle':'Burniță densă','Light freezing drizzle':'Burniță înghețată ușoară','Dense freezing drizzle':'Burniță înghețată densă',
'Light rain':'Ploaie ușoară','Slight rain':'Ploaie ușoară','Moderate rain':'Ploaie moderată','Heavy rain':'Ploaie abundentă','Light freezing rain':'Ploaie înghețată ușoară','Heavy freezing rain':'Ploaie înghețată abundentă',
'Light snowfall':'Ninsoare ușoară','Slight snowfall':'Ninsoare ușoară','Moderate snowfall':'Ninsoare moderată','Heavy snowfall':'Ninsoare abundentă','Snow grains':'Grăunțe de zăpadă',
'Light rain showers':'Averse ușoare','Moderate rain showers':'Averse moderate','Heavy rain showers':'Averse puternice','Violent rain showers':'Averse violente','Light snow showers':'Averse ușoare de ninsoare','Heavy snow showers':'Averse puternice de ninsoare',
'Thunderstorm':'Furtună','Thunderstorm with hail':'Furtună cu grindină','Thunderstorm with slight hail':'Furtună cu grindină ușoară','Heavy thunderstorm':'Furtună puternică','Thunderstorm with heavy hail':'Furtună cu grindină puternică','Weather condition unavailable':'Condiții meteo indisponibile'
};
const key=value=>value.trim().replace(/\s+/g,' ');
function translated(source){
 const value=key(source);if(locale==='en')return source;
 let result=ro[value];
 if(result===undefined){
  let match;
  if((match=value.match(/^([✓!?]) (LOW RISK|MODERATE RISK|HIGH RISK|NO CURRENT READING)(.*)$/)))result=match[1]+' '+ro[match[2]]+match[3].replace('Sample data',ro['Sample data']).replace('API reading','Citire din API');
  else if((match=value.match(/^(Living room|Bedroom|Kitchen|Device) · (.*)$/)))result=ro[match[1]]+' · '+(ro[match[2]]||match[2]);
  else if((match=value.match(/^(Sample|Reading) at (.*?) · (\d+)(s ago| min old)$/)))result=(match[1]==='Sample'?'Exemplu':'Citire')+' la '+match[2]+' · acum '+match[3]+(match[4]==='s ago'?' s':' min');
  else if((match=value.match(/^(Sample data|API mode) · Refresh every 15 seconds$/)))result=ro[match[1]]+' · Actualizare la fiecare 15 secunde';
  else if(value==='Project prototype · Sample data · Refreshes every 15 seconds')result='Prototip de proiect · Date demonstrative · Actualizare la fiecare 15 secunde';
  else if((match=value.match(/^(\d+) readings checked in the whole chain\.$/)))result=match[1]+' citiri verificate în întregul lanț.';
  else if((match=value.match(/^Chain mismatch at reading (.*?)\.$/)))result='Neconcordanță în lanț la citirea '+match[1]+'.';
  else if((match=value.match(/^Humidity over the last 24 hours; latest (.*?) percent\.$/)))result='Umiditatea în ultimele 24 de ore; ultima valoare '+match[1]+'%.';
  else if((match=value.match(/^(.*?), (-?[\d.]+ °C)$/))&&ro[match[1]])result=ro[match[1]]+', '+match[2];
  else if((match=value.match(/^(Illustrative forecast\.|Forecast for London\.) (?:Updated (.*?)\. )?Next (.*?) hours\. Weather data: Open-Meteo\.$/)))result=(match[1]==='Illustrative forecast.'?'Prognoză demonstrativă. ':'Prognoză pentru Londra. ')+(match[2]?'Actualizată la '+match[2]+'. ':'')+'Următoarele '+match[3]+' de ore. Sursa meteo: Open-Meteo.';
  else if((match=value.match(/^(.*?) · recent readings$/)))result=match[1]+' · citiri recente';
  else if((match=value.match(/^Live API mode\. (.*)$/)))result='Mod API live. '+match[1].replace(/^Source: /,'Sursa: ').replace('Requests use the same origin.','Cererile folosesc aceeași origine.');
  else if((match=value.match(/^Requesting explanation in (.*?)…$/)))result='Se solicită explicația în '+match[1]+'…';
  else if((match=value.match(/^Sample explanation in (.*?)\. No API request was made in demo mode\.$/)))result='Explicație demonstrativă în '+match[1]+'. În modul demonstrativ nu a fost trimisă o cerere API.';
  else if((match=value.match(/^Explanation returned for (.*?)\.$/)))result='Explicație primită pentru '+match[1]+'.';
  else if((match=value.match(/^This report contains sample data\. (.*)$/)))result='Acest raport conține date demonstrative. '+(ro[match[1]]||translateNotice(match[1]));
  else if(value.startsWith('Review the letter, then use the browser print dialog'))result=translateNotice(value);
  else if((match=value.match(/^(Forecast unavailable\.|History unavailable\.) (.*)$/)))result=(match[1]==='Forecast unavailable.'?'Prognoză indisponibilă. ':'Istoric indisponibil. ')+match[2];
  else if(value.endsWith('. Check that the API is running.'))result=value.replace(/\. Check that the API is running\.$/,'. Verifică dacă API-ul este pornit.');
  else if(value.endsWith('. This is not a verified result.'))result=value.replace(/\. This is not a verified result\.$/,'. Acesta nu este un rezultat verificat.');
 }
 if(result===undefined)return source;
 return (source.match(/^\s*/)?.[0]||'')+result+(source.match(/\s*$/)?.[0]||'');
}
function translateNotice(value){return value==='Review the letter, then use the browser print dialog to save a PDF. No letter is sent automatically.'?'Verifică scrisoarea, apoi folosește fereastra de tipărire pentru a salva un PDF. Scrisoarea nu este trimisă automat.':value;}
function apply(doc){
 if(!doc.body)return;
 doc.documentElement.lang=locale;
 const walker=doc.createTreeWalker(doc.body,4);let node;
 while((node=walker.nextNode())){
  if(!node.parentElement||node.parentElement.closest('script,style,textarea,#print-letter,#report-explanation'))continue;
  let record=textRecords.get(node);
  if(!record||node.nodeValue!==record.last)record={source:node.nodeValue};
  const value=translated(record.source);if(node.nodeValue!==value)node.nodeValue=value;
  record.last=value;textRecords.set(node,record);
 }
 for(const el of doc.body.querySelectorAll('[aria-label],[alt],[title]')){
  const records=attributeRecords.get(el)||{};
  for(const attr of ['aria-label','alt','title']){
   if(!el.hasAttribute(attr))continue;
   const current=el.getAttribute(attr);let record=records[attr];
   if(!record||current!==record.last)record={source:current};
   const value=translated(record.source);if(value!==current)el.setAttribute(attr,value);
   record.last=value;records[attr]=record;
  }
  attributeRecords.set(el,records);
 }
 doc.title=locale==='ro'?(doc.title.includes('standalone')||doc.title.includes('independentă')?ro['MouldShield - standalone preview']:ro['MouldShield · Your home, in view']):(doc.title.includes('standalone')||doc.title.includes('independentă')?'MouldShield - standalone preview':'MouldShield · Your home, in view');
}
return {get locale(){return locale;},setLanguage(value){locale=value==='ro'?'ro':'en';return locale;},text:translated,apply};
});
