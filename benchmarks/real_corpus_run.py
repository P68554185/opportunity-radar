import os,sys,json,tempfile
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,ROOT)
sys.path.insert(0,os.path.join(ROOT,"benchmarks"))
from sync import sync_json
from engine import trade_opportunities
from quality import report

inp=os.path.join(ROOT,"real_data","bavaria_verified_events.json")
with tempfile.TemporaryDirectory() as d:
    projects=sync_json(inp,os.path.join(d,"real.sqlite"),os.path.join(d,"checkpoint.json"))
    raw=json.load(open(inp,encoding="utf-8"))
    unique=len({x["source_id"] for x in raw})
    opp=sum(1 for p in projects for _ in trade_opportunities(p))
    r=report(len(raw),unique,projects,[],opp)
    r["corpus_kind"]="official_verified_real_data"
    r["verified_source_pages"]=len({x["source_url"] for x in raw})
    print(json.dumps(r,indent=2,ensure_ascii=False))
