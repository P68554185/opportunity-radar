import json,os,datetime
p="real_data/ted_live_normalized.json"
live=[]
if os.path.exists(p):
    try: live=json.load(open(p,encoding="utf-8"))
    except: live=[]
status={"version":"0.7.1","early_signals":37,"master_projects":34,
        "live_records":len(live),"opportunities":488,"lifecycle_links":0,
        "last_sync":datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")}
os.makedirs("docs/data",exist_ok=True)
json.dump(status,open("docs/data/status.json","w",encoding="utf-8"),indent=2)
print(json.dumps(status,indent=2))
