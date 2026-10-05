"""Build enriched Opportunity Intelligence records from normalized TED notices."""
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

def lifecycle_link_score(e,x):
 # Municipality is the strongest project identity signal. Authority names often differ
 # between funding owner and procurement office, so use them as secondary evidence.
 ec,xc=norm(e.get("city","")),norm(x.get("city",""))
 if ec and xc and ec!=xc:return 0.0,{}
 city=1.0 if ec and xc and ec==xc else 0.0
 pt=1.0 if e.get("project_type") and x.get("project_type") and e["project_type"]==x["project_type"] else 0.0
 title=sim(e.get("title",""),x.get("title",""))
 auth=SequenceMatcher(None,norm(e.get("authority","")),norm(x.get("authority",""))).ratio() if x.get("authority") else 0
 score=.48*city+.22*pt+.22*title+.08*auth
 return min(1,score),{"city":round(city,2),"project_type":round(pt,2),"title":round(title,3),"authority":round(auth,3)}

def body_obj(x):
 try:return json.loads(x.get("body") or "{}")
 except Exception:return {}

def opportunity_score(x):
 score=42
 if x.get("project_type"): score+=18
 score+=min(24,6*len(x.get("_trades",[])))
 if x.get("authority"): score+=8
 if x.get("city"): score+=8
 return min(100,score)

def enrich(x):
 b=body_obj(x); score=opportunity_score(x)
 cpv=b.get("cpv",[])
 desc=" ".join(str(v) for v in [x.get("title") or "",x.get("authority") or "",b.get("place") or ""] if v)
 return {
  "source_id":x.get("source_id"),"notice_id":x.get("external_id"),"source_url":x.get("source_url"),
  "published":x.get("published"),"title":x.get("title"),"description":desc,
  "authority":x.get("authority"),"city":x.get("city"),"region":x.get("region"),"country":x.get("country"),
  "project_type":x.get("project_type") or "","trades":x.get("_trades",[]),"cpv":cpv,
  "phase":x.get("phase"),"score":score,"confidence":score/100,
  "band":"HOT" if score>=85 else ("UPCOMING" if score>=65 else "EARLY"),
  "evidence":{"project_type":bool(x.get("project_type")),"trade":bool(x.get("_trades")),"cpv":bool(cpv),"source":"TED live"}
 }

def build():
 live=load(os.path.join(ROOT,"real_data","ted_live_normalized.json"),[])
 early=load(os.path.join(ROOT,"real_data","bavaria_verified_events.json"),[])
 enriched=[enrich(x) for x in live]
 opp=[x for x in enriched if x.get("project_type") or x.get("trades")]
 opp.sort(key=lambda x:(x["score"],x.get("published") or ""),reverse=True)
 links=[]
 for e in early:
  candidates=[]
  for x in live:
   if e.get("project_type") and x.get("project_type") and e["project_type"]!=x["project_type"]: continue
   s,evidence=lifecycle_link_score(e,x)
   # >=0.60 means a strong municipality/type/title combination. Auto-link stays strict.
   if s>=.60:candidates.append((s,x,evidence))
  if candidates:
   s,x,evidence=max(candidates,key=lambda z:z[0])
   links.append({"early_source_id":e.get("source_id"),"early_title":e.get("title"),"early_city":e.get("city"),
    "live_source_id":x.get("source_id"),"live_title":x.get("title"),"live_city":x.get("city"),
    "score":round(s,3),"status":"review" if s<.84 else "auto_link","evidence":evidence})
 out={"version":"0.9.2","live_records":len(live),"enriched_records":len(enriched),"classified_opportunities":len(opp),"lifecycle_candidates":len(links),"opportunities":opp[:50],"lifecycle_links":links}
 os.makedirs(os.path.join(ROOT,"docs","data"),exist_ok=True); os.makedirs(os.path.join(ROOT,"reports"),exist_ok=True); os.makedirs(os.path.join(ROOT,"real_data"),exist_ok=True)
 with open(os.path.join(ROOT,"real_data","ted_live_enriched.json"),"w",encoding="utf-8") as f:json.dump(enriched,f,ensure_ascii=False,indent=2)
 with open(os.path.join(ROOT,"reports","intelligence_report.json"),"w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,indent=2)
 with open(os.path.join(ROOT,"docs","data","opportunities.json"),"w",encoding="utf-8") as f:json.dump(out,f,ensure_ascii=False,indent=2)
 print(json.dumps({k:v for k,v in out.items() if k not in ("opportunities","lifecycle_links")},ensure_ascii=False,indent=2)); return out
if __name__=="__main__":build()
