"use strict";
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const TRADE_NAMES={electrical:"Elektro",hvac:"Heizung, Lüftung & Klima",plumbing:"Sanitär",drywall:"Trockenbau",painting:"Malerarbeiten",flooring:"Boden & Fliesen",roof:"Dach",windows_doors:"Fenster & Türen",facade:"Fassade",earthworks:"Erdarbeiten & Tiefbau",structural:"Rohbau",landscaping:"Garten- & Landschaftsbau",fire_protection:"Brandschutz",elevator:"Aufzüge",demolition:"Abbruch",roadworks:"Straßenbau",sewer_pipe:"Kanalbau",railworks:"Gleisbau",solar_energy:"Photovoltaik",scaffolding:"Gerüstbau",metalwork:"Metallbau",steelwork:"Stahlbau",screed:"Estrich",building_automation:"Gebäudeautomation",industrial_doors:"Industrietore",medical_technology:"Medizintechnik",elevators:"Aufzüge",building_services:"Gebäudetechnik",plastering:"Putzarbeiten",finishing:"Ausbau"};
const PHASES={idea:"Projektidee",political_decision:"Beschluss gefasst",funding:"Förderung beschlossen",object_planning:"In Planung",specialist_planning:"Fachplanung",execution_planning:"Ausführungsplanung",tender:"In Ausschreibung",award:"Bereits vergeben"};
const EARLY=new Set(["idea","political_decision","funding","object_planning","specialist_planning","execution_planning"]);
const norm=s=>String(s||"").toLocaleLowerCase("de").trim().replace(/\s+/g," ");
const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}};
const storedProfile=read("bauradar.profile.v1",{});
let profile=storedProfile&&typeof storedProfile==="object"&&!Array.isArray(storedProfile)?storedProfile:{};
profile.trades=Array.isArray(profile.trades)?profile.trades.filter(t=>Object.hasOwn(TRADE_NAMES,t)):[];
const storedSaved=read("bauradar.saved.v1",[]);
let saved=new Set(Array.isArray(storedSaved)?storedSaved.filter(x=>typeof x==="string"):[]);
let records=[],view="all",limit=20;
const $=id=>document.getElementById(id);
function persist(key,value){try{localStorage.setItem(key,JSON.stringify(value));return true}catch{$("profileMessage").textContent="Speichern auf diesem Gerät ist nicht verfügbar. Ihre Auswahl gilt für diese Sitzung.";return false}}
function sourceLink(url){try{const u=new URL(url);return u.protocol==="https:"&&["ted.europa.eu","www.stmfh.bayern.de"].includes(u.hostname)?u.href:""}catch{return ""}}
function dateLabel(date){const d=new Date(date);return Number.isNaN(d.valueOf())?"Datum unbekannt":new Intl.DateTimeFormat("de-DE").format(d)}
$("companyName").value=typeof profile.name==="string"?profile.name:"";
$("companyCity").value=typeof profile.city==="string"?profile.city:"";
$("locationMode").value=profile.locationMode==="city"?"city":"all";
$("tradeChoices").innerHTML=Object.entries(TRADE_NAMES).filter(([t])=>!["elevators","medical_technology","steelwork","screed","industrial_doors","building_automation","building_services","plastering","finishing"].includes(t)).map(([t,n])=>`<label><input type="checkbox" name="trade" value="${esc(t)}" ${profile.trades.includes(t)?"checked":""}><span>${esc(n)}</span></label>`).join("");
$("profileForm").addEventListener("submit",event=>{
 event.preventDefault();
 const city=$("companyCity").value.trim(),locationMode=$("locationMode").value;
 if(locationMode==="city"&&!city){$("profileMessage").textContent="Bitte geben Sie einen Ort ein oder wählen Sie deutschlandweit.";return}
 profile={name:$("companyName").value.trim(),city,locationMode,trades:[...document.querySelectorAll('[name="trade"]:checked')].map(e=>e.value)};
 const ok=persist("bauradar.profile.v1",profile);
 if(ok)$("profileMessage").textContent="Profil auf diesem Gerät gespeichert.";
 limit=20;render();
});
document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{
 view=button.dataset.view;limit=20;
 document.querySelectorAll("[data-view]").forEach(b=>{b.classList.toggle("active",b===button);b.setAttribute("aria-pressed",String(b===button))});render();
}));
["phaseFilter","search"].forEach(id=>$(id).addEventListener("input",()=>{limit=20;render()}));
$("loadMore").addEventListener("click",()=>{limit+=20;render()});
$("feed").addEventListener("click",event=>{
 const button=event.target.closest("[data-watch]");if(!button)return;
 const id=button.dataset.watch;saved.has(id)?saved.delete(id):saved.add(id);
 persist("bauradar.saved.v1",[...saved]);render();
});
function selectedTrades(record){
 const t=record.trades||[];
 return profile.trades.length?t.filter(x=>profile.trades.includes(x)):t;
}
function card(record){
 const early=EARLY.has(record.phase),url=sourceLink(record.source_url),watch=saved.has(record.id);
 const trades=selectedTrades(record).slice(0,6);
 const priority=record.phase==="award"?"Zur Marktbeobachtung":early?"Frühzeitig Kontakt aufnehmen":"Unterlagen jetzt prüfen";
 return `<article class="project-card"><div class="card-top"><span class="phase ${early?"early":record.phase==="tender"?"tender":""}">${esc(PHASES[record.phase]||"Phase noch offen")}</span><span class="priority">${esc(priority)}</span></div>
 <h3>${esc(record.title)}</h3><p class="location">${esc(record.city||"Projektort noch offen")}${record.region?" · "+esc(record.region):""}</p>
 <dl class="facts"><div><dt>Auftraggeber</dt><dd>${esc(record.authority||"Noch nicht bekannt")}</dd></div><div><dt>Ausschreibung</dt><dd>${record.phase==="tender"?"Bereits veröffentlicht · Frist in der Quelle prüfen":record.phase==="award"?"Auftrag bereits vergeben":"Zeitraum noch nicht veröffentlicht"}</dd></div><div><dt>Veröffentlicht</dt><dd>${esc(dateLabel(record.published))}</dd></div></dl>
 <div class="trade-chips">${trades.map(t=>`<span>${esc(TRADE_NAMES[t]||t)}</span>`).join("")}</div>
 <p class="trade-note">${record.trade_basis==="project_type_expected"?"Mögliche Gewerke aus der Projektart; konkrete Lose noch offen.":"Gewerke aus der Vergabemeldung abgeleitet."}</p>
 <div class="action"><strong>Ihr nächster Schritt</strong>${esc(record.next_action||"Details beim Auftraggeber oder in der Quelle prüfen.")}</div>
 <div class="card-footer">${url?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Originalquelle ansehen ↗</a>`:"<span>Quelle nicht verfügbar</span>"}<button class="watch" data-watch="${esc(record.id)}" aria-pressed="${watch}">${watch?"✓ Beobachtet":"＋ Beobachten"}</button></div></article>`;
}
function render(){
 const query=norm($("search").value),phase=$("phaseFilter").value;
 const rows=records.filter(r=>(!profile.trades.length||selectedTrades(r).length)
  &&(profile.locationMode!=="city"||norm(r.city)===norm(profile.city))
  &&(view!=="early"||EARLY.has(r.phase))&&(view!=="saved"||saved.has(r.id))
  &&(!phase||r.phase===phase)&&(!query||norm([r.title,r.city,r.authority].join(" ")).includes(query)))
  .sort((a,b)=>Number(b.phase!=="award")-Number(a.phase!=="award")||Number(EARLY.has(b.phase))-Number(EARLY.has(a.phase))||String(b.published).localeCompare(String(a.published)));
 $("resultCount").textContent=rows.length+" passende "+(rows.length===1?"Chance":"Chancen")+(profile.locationMode==="city"?" in "+profile.city:" in Deutschland");
 $("savedCount").textContent=saved.size;
 $("feed").innerHTML=rows.length?rows.slice(0,limit).map(card).join(""):`<p class="empty">${view==="saved"?"Noch keine passenden Projekte in Ihrer Merkliste. Wählen Sie bei einem Projekt „Beobachten“.":"Keine passenden Projekte gefunden. Erweitern Sie Ihr Suchgebiet oder wählen Sie weitere Gewerke."}</p>`;
 $("loadMore").hidden=rows.length<=limit;
}
async function init(){
 try{
  const response=await fetch("data/bauradar_feed.json",{cache:"no-store"});if(!response.ok)throw Error("feed");
  const data=await response.json();if(!Array.isArray(data.opportunities))throw Error("schema");
  records=data.opportunities.filter(r=>["CONFIDENT","VERIFIED_EARLY"].includes(r.quality_status)&&r.id&&Array.isArray(r.trades));render();
  const status=await fetch("data/status.json",{cache:"no-store"});if(status.ok){const d=await status.json();$("lastUpdate").textContent=d.last_sync?"Datenstand: "+d.last_sync:""}
 }catch{$("feed").innerHTML='<p class="empty">Die Projekte konnten gerade nicht geladen werden. Bitte versuchen Sie es später erneut.</p>';$("resultCount").textContent="Projekte derzeit nicht verfügbar."}
}
init();
