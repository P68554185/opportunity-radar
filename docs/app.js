fetch("data/status.json?"+Date.now()).then(r=>r.json()).then(d=>{
 const set=(id,v)=>document.getElementById(id).textContent=v;
 set("projects",d.master_projects??34);set("early",d.early_signals??37);set("live",d.live_records??0);
 set("opps",d.opportunities??488);set("links",d.lifecycle_links??0);
 set("sync","Letzter Sync: "+(d.last_sync||"noch keiner"));
 const n=d.live_records||0;document.getElementById("bar").style.width=Math.min(100,n/5)+"%";
 set("progressText",n+" / 500");set("tedStatus",n>0?"AKTIV":"BEREIT");
}).catch(()=>{});