"""Turn normalized live notices into dashboard-ready opportunities and EARLY lifecycle candidates."""
import json, os, re
from difflib import SequenceMatcher
ROOT=os.path.dirname(os.path.dirname(__file__))

def load(path, default):
 try:
  with open(path,encoding="utf-8") as f:return json.load(f)
 except Exception:return default

def norm(s): return " ".join(re.sub(r"[^a-z0-9äöüß ]+"," ",(s or "").lower()).split())
def tok(s): return {x for x in norm(s).split() if len(x)>3 and x not in {"neubau","umbau","sanierung","erweiterung","arbeiten","bauarbeiten"}}
def sim(a,b):
 A,B=tok(a),tok(b); j=len(A&B)/len(A|B) if A|B else 0
 return .55*j+.45*SequenceMatcher(None,norm(a),norm(b)).ratio()

def opportunity_score(x):
 score=42
 if x.get("project_type"): score+=18
 score+=min(24,6*len(x.get("_trades",[])))
 if x.get("authority"): score+=8
 if x.get("city"): score+=8
 return min(100,score)

def build():
 live=load(os.path.join(ROOT,"real_data","ted_live_normalized.json"),[])
 early=load(os.path.join(ROOT,"real_data","bavaria_verified_events.json"),[])
 opp=[]
 for x in live:
  if not (x.get("project_type") or x.get("_trades")): continue
  y={k:x.get(k) for k in ("source_id","source_url","published","title","authority","city","region","country","project_type","phase")}
  y["trades"]=x.get("_trades",[]); y["score"]=opportunity_score(x)
  y["band"]="HOT" if y["score"]>=85 else ("UPCOMING" if y["score"]>=65 else "EARLY")
  opp.append(y)
 opp.sort(key=lambda x:(x["score"],x.get("published") or ""),reverse=True)
 links=[]
 for e in early:
  candidates=[]
  for x in live:
   if e.get("project_type") and x.get("project_type") and e["project_type"]!=x["project_type"]: continue
   title_score=sim(e.get("title",""),x.get("title",""))
   auth_score=SequenceMatcher(None,norm(e.get("authority","")),norm(x.get("authority",""))).ratio() if x.get("authority") else 0
   city_bonus=.30 if e.get("city") and x.get("city") and norm(e["city"])==norm(x["city"]) else 0
   s=min(1,.55*title_score+.15*auth_score+city_bonus)
   if s>=.58:candidates.append((s,x))
  if candidates:
   s,x=max(candidates,key=lambda z:z[0])
   links.append({"early_source_id":e.get("source_id"),"early_title":e.get("title"),"live_source_id":x.get("source_id"),"live_title":x.get("title"),"score":round(s,3),"status":"review" if s<.82 else "auto_link"})
 out={"live_records":len(live),"classified_opportunities":len(opp),"lifecycle_candidates":len(links),"opportunities":opp[:50],"lifecycle_links":links}
 os.makedirs(os.path.join(ROOT,"docs","data"),exist_ok=True)
 for path in [os.path.join(ROOT,"reports","intelligence_report.json"),os.path.join(ROOT,"docs","data","opportunities.json")]:
  with open(path,"w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,indent=2)
 print(json.dumps({k:v for k,v in out.items() if k not in ("opportunities","lifecycle_links")},ensure_ascii=False,indent=2))
 return out
if __name__=="__main__":build()
