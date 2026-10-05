import os, sys, json, datetime
ROOT = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "live"))
from ted_fetch import LiveTedFetcher
from normalize import normalize

os.makedirs(os.path.join(ROOT, "reports"), exist_ok=True);os.makedirs(os.path.join(ROOT, "real_data"), exist_ok=True)
notices, errors = LiveTedFetcher(os.path.join(ROOT, "real_data", "ted_live_raw")).fetch(500, 2)
norm=[]
for n in notices:
 try:norm.append(normalize(n))
 except Exception as ex:errors.append({"type":"normalize","message":repr(ex)})
classified=sum(bool(x.get("project_type")) for x in norm);traded=sum(bool(x.get("_trades")) for x in norm)
status="complete" if len(norm)>=500 else ("partial" if norm else "failed")
rep={"requested":500,"downloaded_live":len(notices),"normalized":len(norm),"project_type_classified":classified,"trade_classified":traded,"errors":errors,"status":status,"run_at":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
with open(os.path.join(ROOT,"reports","live_ted_500_report.json"),"w",encoding="utf-8") as f:json.dump(rep,f,ensure_ascii=False,indent=2)
if norm:
 with open(os.path.join(ROOT,"real_data","ted_live_normalized.json"),"w",encoding="utf-8") as f:json.dump(norm,f,ensure_ascii=False,indent=2)
print(json.dumps(rep,ensure_ascii=False,indent=2))
if not norm:raise SystemExit(2)
