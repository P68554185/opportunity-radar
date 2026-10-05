const esc=s=>String(s??"").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
Promise.all([
 fetch("data/status.json?"+Date.now()).then(r=>r.json()),
 fetch("data/opportunities.json?"+Date.now()).then(r=>r.ok?r.json():{opportunities:[]}).catch(()=>({opportunities:[]}))
]).then(([d,o])=>{
 const set=(id,v)=>{const e=document.getElementById(id);if(e)e.textContent=v};
 set("projects",d.master_projects??34);set("early",d.early_signals??37);set("live",d.live_records??0);
 set("classified",d.classified_opportunities??0);set("links",d.lifecycle_links??0);
 set("sync","Letzter Sync: "+(d.last_sync||"noch keiner"));
 const n=d.live_records||0;document.getElementById("bar").style.width=Math.min(100,n/5)+"%";
 set("progressText",n+" / 500");set("tedStatus",n>0?"AKTIV":"BEREIT");
 const feed=document.getElementById("feed"), rows=(o.opportunities||[]).slice(0,12);
 if(!rows.length){feed.innerHTML='<div class="empty">Noch keine klassifizierten Live Opportunities.</div>';return}
 feed.innerHTML=rows.map(x=>`<article class="opp"><div class="oppTop"><span class="band ${esc((x.band||'EARLY').toLowerCase())}">${esc(x.band)}</span><strong>${esc(x.score)}%</strong></div><h4>${esc(x.title)}</h4><div class="meta">${esc(x.project_type||'Bauprojekt')} · ${esc(x.phase||'tender')} ${x.city?'· '+esc(x.city):''}</div><div class="chips">${(x.trades||[]).slice(0,5).map(t=>`<span>${esc(t)}</span>`).join('')}</div><div class="source">${esc(x.authority||'TED')} · ${esc(x.published||'')}</div></article>`).join('');
}).catch(()=>{});
