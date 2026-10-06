"use strict";
const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const TRADE_NAMES={insulation:"Dämmung",fencing:"Zäune & Geländer",electrical:"Elektro",hvac:"Heizung, Lüftung & Klima",plumbing:"Sanitär",drywall:"Trockenbau",painting:"Malerarbeiten",flooring:"Boden & Fliesen",roof:"Dach",windows_doors:"Fenster & Türen",facade:"Fassade",earthworks:"Erdarbeiten & Tiefbau",structural:"Rohbau",landscaping:"Garten- & Landschaftsbau",fire_protection:"Brandschutz",elevator:"Aufzüge",demolition:"Abbruch",roadworks:"Straßenbau",sewer_pipe:"Kanalbau",railworks:"Gleisbau",solar_energy:"Photovoltaik",scaffolding:"Gerüstbau",metalwork:"Metallbau",steelwork:"Stahlbau",screed:"Estrich",building_automation:"Gebäudeautomation",industrial_doors:"Industrietore",medical_technology:"Medizintechnik",elevators:"Aufzüge",building_services:"Gebäudetechnik",plastering:"Putzarbeiten",finishing:"Ausbau"};
const PHASES={procurement:"Vergaben veröffentlicht",project_announced:"Bauvorhaben angekündigt",idea:"Projektidee",political_decision:"Beschluss gefasst",funding:"Förderung beschlossen",prior_information:"Ausschreibung angekündigt",object_planning:"In Planung",specialist_planning:"Fachplanung",execution_planning:"Ausführungsplanung",tender:"In Ausschreibung",award:"Bereits vergeben"};
const EARLY=new Set(["project_announced","idea","political_decision","funding","prior_information","object_planning","specialist_planning","execution_planning"]);
const norm=s=>String(s||"").toLocaleLowerCase("de").trim().replace(/\s+/g," ");
const read=(key,fallback)=>{try{return JSON.parse(localStorage.getItem(key))??fallback}catch{return fallback}};
const storedProfile=read("bauradar.profile.v1",{});
let profile=storedProfile&&typeof storedProfile==="object"&&!Array.isArray(storedProfile)?storedProfile:{};
profile.trades=Array.isArray(profile.trades)?profile.trades.filter(t=>Object.hasOwn(TRADE_NAMES,t)):[];
const storedSaved=read("bauradar.saved.v1",[]);
let saved=new Set(Array.isArray(storedSaved)?storedSaved.filter(x=>typeof x==="string"):[]);
let records=[],view="all",limit=20,account=null,backend=false;
async function api(path,method="GET",body){
 const r=await fetch("api/"+path,{method,headers:body?{"Content-Type":"application/json"}:{},credentials:"same-origin",body:body?JSON.stringify(body):undefined});
 const d=await r.json().catch(()=>({}));
 if(!r.ok)throw Error(typeof d.detail==="string"?d.detail:"Bitte prüfen Sie Ihre Angaben und versuchen Sie es erneut.");
 return d;
}
const $=id=>document.getElementById(id);
function persist(key,value){try{localStorage.setItem(key,JSON.stringify(value));return true}catch{$("profileMessage").textContent="Speichern auf diesem Gerät ist nicht verfügbar. Ihre Auswahl gilt für diese Sitzung.";return false}}
function sourceLink(url){try{const u=new URL(url);return u.protocol==="https:"&&["ted.europa.eu","www.stmfh.bayern.de","www.kkh-alsfeld.de","hibb.hamburg.de"].includes(u.hostname)?u.href:""}catch{return ""}}
function dateLabel(date){const d=new Date(date);return Number.isNaN(d.valueOf())?"Datum unbekannt":new Intl.DateTimeFormat("de-DE").format(d)}
$("companyName").value=typeof profile.name==="string"?profile.name:"";
$("companyCity").value=typeof profile.city==="string"?profile.city:"";
$("locationMode").value=profile.locationMode==="city"?"city":"all";
$("tradeChoices").innerHTML=Object.entries(TRADE_NAMES).filter(([t])=>!["elevators","medical_technology","steelwork","screed","industrial_doors","building_automation","building_services","plastering","finishing"].includes(t)).map(([t,n])=>`<label><input type="checkbox" name="trade" value="${esc(t)}" ${profile.trades.includes(t)?"checked":""}><span>${esc(n)}</span></label>`).join("");
$("profileForm").addEventListener("submit",async event=>{
 event.preventDefault();
 const city=$("companyCity").value.trim(),locationMode=$("locationMode").value;
 if(locationMode==="city"&&!city){$("profileMessage").textContent="Bitte geben Sie einen Ort ein oder wählen Sie deutschlandweit.";return}
 const next={...profile,name:$("companyName").value.trim(),city,locationMode,trades:[...document.querySelectorAll('[name="trade"]:checked')].map(e=>e.value)};
 if(account){try{profile=await api("profile","PUT",next);$("profileMessage").textContent="Betriebsprofil gespeichert."}catch(error){$("profileMessage").textContent=error.message;return}}
 else{profile=next;const ok=persist("bauradar.profile.v1",profile);if(ok)$("profileMessage").textContent="Profil auf diesem Gerät gespeichert."}
 limit=20;render();
});
document.querySelectorAll("[data-view]").forEach(button=>button.addEventListener("click",()=>{
 view=button.dataset.view;limit=20;
 document.querySelectorAll("[data-view]").forEach(b=>{b.classList.toggle("active",b===button);b.setAttribute("aria-pressed",String(b===button))});render();
}));
["phaseFilter","search"].forEach(id=>$(id).addEventListener("input",()=>{limit=20;render()}));
$("loadMore").addEventListener("click",()=>{limit+=20;render()});
$("feed").addEventListener("click",async event=>{
 const button=event.target.closest("[data-watch]");if(!button)return;
 const id=button.dataset.watch;button.disabled=true;
 const record=records.find(r=>r.id===id),watched=record?watchIds(record):[id].filter(key=>saved.has(key));
 if(account){try{
  if(watched.length){for(const key of watched)await api("watches/"+encodeURIComponent(key),"DELETE")}
  else await api("watches/"+encodeURIComponent(id),"PUT");
 }catch(error){$("profileMessage").textContent=error.message;button.disabled=false;return}}
 if(watched.length){for(const key of watched)saved.delete(key)}else saved.add(id);
 if(!account)persist("bauradar.saved.v1",[...saved]);render();
});
function watchIds(record){return [record.id,...(record.aliases||[])].filter(id=>saved.has(id))}
function hasWatch(record){return watchIds(record).length>0}
function selectedTrades(record){
 const t=record.trades||[];
 return profile.trades.length?t.filter(x=>profile.trades.includes(x)):t;
}
function projectHistory(record){
 const events=Array.isArray(record.project_history)?record.project_history:[];
 if(events.length<2)return "";
 const rows=events.map(event=>{
  const url=sourceLink(event.source_url);
  return `<li><time>${esc(dateLabel(event.published))}</time><span>${esc(PHASES[event.phase]||"Projektmeldung")}</span><span class="history-title">${esc(event.title||"")}</span>${url?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Quelle ↗</a>`:""}</li>`;
 }).join("");
 return `<details class="project-history"><summary>Entwicklung des Bauvorhabens ansehen</summary><ol>${rows}</ol><p>Frühere öffentliche Meldungen zum Projekt. Vergabezeiträume bitte in der aktuellen Quelle prüfen.</p></details>`;
}
function card(record){
 const early=EARLY.has(record.phase),url=sourceLink(record.source_url),watch=hasWatch(record);
 const trades=selectedTrades(record).slice(0,6);
 const priority=record.phase==="award"?"Zur Marktbeobachtung":early?"Frühzeitig Kontakt aufnehmen":record.phase==="tender"?"Unterlagen jetzt prüfen":"Projektphase klären";
 return `<article class="project-card"><div class="card-top"><span class="phase ${early?"early":record.phase==="tender"?"tender":""}">${esc(PHASES[record.phase]||"Phase noch offen")}</span><span class="priority">${esc(priority)}</span></div>
 <h3>${esc(record.title)}</h3><p class="location">${esc(record.city||"Projektort noch offen")}${record.region?" · "+esc(record.region):""}</p>
 <dl class="facts"><div><dt>Auftraggeber</dt><dd>${esc(record.authority||"Noch nicht bekannt")}</dd></div><div><dt>Ausschreibung</dt><dd>${record.phase==="tender"?"Bereits veröffentlicht · Frist in der Quelle prüfen":record.phase==="award"?"Auftrag bereits vergeben":record.phase==="procurement"?"Einzelne Vergabemeldungen und Fristen prüfen":"Zeitraum noch unbekannt"}</dd></div><div><dt>Veröffentlicht</dt><dd>${esc(dateLabel(record.published))}</dd></div></dl>
 <div class="trade-chips">${trades.map(t=>`<span>${esc(TRADE_NAMES[t]||t)}</span>`).join("")}</div>
 <p class="trade-note">${record.trade_basis==="project_type_expected"?"Mögliche Gewerke aus der Projektart; konkrete Lose noch offen.":"Gewerke aus der Vergabemeldung abgeleitet."}</p>
 <div class="action"><strong>Ihr nächster Schritt</strong>${esc(record.next_action||"Details beim Auftraggeber oder in der Quelle prüfen.")}</div>
 ${projectHistory(record)}
 <div class="card-footer">${url?`<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Originalquelle ansehen ↗</a>`:"<span>Quelle nicht verfügbar</span>"}<button class="watch" data-watch="${esc(record.id)}" aria-pressed="${watch}">${watch?"✓ Beobachtet":"＋ Beobachten"}</button></div></article>`;
}
function render(){
 const query=norm($("search").value),phase=$("phaseFilter").value;
 const rows=records.filter(r=>(!profile.trades.length||selectedTrades(r).length)
  &&(profile.locationMode!=="city"||norm(r.city)===norm(profile.city))
  &&(view!=="early"||EARLY.has(r.phase))&&(view!=="saved"||hasWatch(r))
  &&(!phase||r.phase===phase)&&(!query||norm([r.title,r.city,r.authority].join(" ")).includes(query)))
  .sort((a,b)=>Number(b.phase!=="award")-Number(a.phase!=="award")||Number(EARLY.has(b.phase))-Number(EARLY.has(a.phase))||String(b.published).localeCompare(String(a.published)));
 $("resultCount").textContent=rows.length+" passende "+(rows.length===1?"Chance":"Chancen")+(profile.locationMode==="city"?" in "+profile.city:" in Deutschland");
 $("savedCount").textContent=new Set([...saved].map(id=>records.find(r=>r.id===id||(r.aliases||[]).includes(id))?.id||id)).size;
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
function fillProfile(){
 $("companyName").value=profile.name||"";$("companyCity").value=profile.city||"";
 $("locationMode").value=profile.locationMode||"all";
 document.querySelectorAll('[name="trade"]').forEach(e=>e.checked=(profile.trades||[]).includes(e.value));
}
async function loadAccount(){
 const current=await api("me");
 const [serverProfile,serverWatches]=await Promise.all([api("profile"),api("watches")]);
 account=current;profile=serverProfile;saved=new Set(serverWatches);fillProfile();render();
 $("profileHint").textContent="Angemeldet als "+account.email+". Profil und Merkliste werden in Ihrem Konto gespeichert.";
 $("accountOpen").hidden=true;$("logout").hidden=false;$("accountPanel").hidden=true;
 $("accountPassword").value="";
}
async function initAccount(){
 try{
  const health=await api("health");if(health.status!=="ok")return;backend=true;
  $("accountOpen").hidden=false;$("register").hidden=!health.signup_enabled;
  await loadAccount();
 }catch{}
}
$("accountOpen").addEventListener("click",()=>{$("accountPanel").hidden=false;$("accountEmail").focus()});
$("accountClose").addEventListener("click",()=>{$("accountPanel").hidden=true});
async function authenticate(register=false){
 $("accountMessage").textContent="Bitte warten …";
 try{await api(register?"register":"login","POST",{email:$("accountEmail").value,password:$("accountPassword").value});await loadAccount();$("accountMessage").textContent=""}
 catch(error){$("accountMessage").textContent=error.message}
}
$("accountForm").addEventListener("submit",event=>{event.preventDefault();authenticate()});
$("register").addEventListener("click",()=>{if($("accountForm").reportValidity())authenticate(true)});
$("logout").addEventListener("click",async()=>{
 try{await api("logout","POST");account=null;profile={trades:[],locationMode:"all"};saved=new Set();fillProfile();render();
 $("profileHint").textContent="Abgemeldet. Neue Auswahl bleibt auf diesem Gerät.";$("logout").hidden=true;$("accountOpen").hidden=false;
 }catch(error){$("profileMessage").textContent=error.message}
});
init();
initAccount();
