
from __future__ import annotations
import csv, json, random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT/"reports"; REPORTS.mkdir(exist_ok=True)
DOCS = ROOT/"docs"/"data"; DOCS.mkdir(parents=True, exist_ok=True)
REAL = ROOT/"real_data"

def load(p):
    try: return json.loads(p.read_text(encoding="utf-8"))
    except Exception: return None

def records_from(obj):
    if isinstance(obj, list): return obj
    if isinstance(obj, dict):
        for k in ("opportunities","records","notices","items","feed"):
            if isinstance(obj.get(k), list): return obj[k]
    return []

# Prefer complete normalized acquisition, never the 50-card website feed.
sources = [
    REAL/"ted_live_enriched.json",
    REAL/"ted_live_normalized.json",
    REPORTS/"live_ted_500_normalized.json",
    REPORTS/"live_ted_500.json",
]
records=[]; source=None
for p in sources:
    if p.exists():
        x=records_from(load(p))
        if len(x) >= 100:
            records=x; source=str(p.relative_to(ROOT)); break

# Last resort: locate a JSON dataset >=100 records.
if not records:
    for base in (REAL, REPORTS):
        if not base.exists(): continue
        for p in base.rglob("*.json"):
            x=records_from(load(p))
            if len(x) >= 100:
                records=x; source=str(p.relative_to(ROOT)); break
        if records: break

def val(r,*ks,default=""):
    for k in ks:
        v=r.get(k)
        if v not in (None,"",[],{}): return v
    return default

def arr(v):
    return v if isinstance(v,list) else ([] if v in (None,"") else [v])

import sys
sys.path.insert(0, str(ROOT))
from intelligence.evidence import classify_evidence

evaluated=[]
for r in records:
    if not isinstance(r,dict): continue
    status,evidence=classify_evidence(r)
    evaluated.append({"record":r,"status":status,"evidence":evidence})

counts=Counter(x["status"] for x in evaluated)

# deterministic stratified sample, max 60
rng=random.Random(805)
sample=[]
targets={"CONFIDENT":20,"REVIEW":25,"UNKNOWN":15}
for status,n in targets.items():
    b=[x for x in evaluated if x["status"]==status]; rng.shuffle(b); sample += b[:n]
if len(sample)<min(60,len(evaluated)):
    ids={id(x) for x in sample}
    rest=[x for x in evaluated if id(x) not in ids]; rng.shuffle(rest)
    sample += rest[:60-len(sample)]

fields=["audit_id","notice_id","title","description","cpv","project_type_predicted",
        "trades_predicted","confidence","quality_status","evidence",
        "project_type_correct","trades_correct","false_positive","review_notes"]
with (REPORTS/"quality_audit_sample.csv").open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for i,x in enumerate(sample,1):
        r=x["record"]; e=x["evidence"]
        w.writerow({
            "audit_id":i,"notice_id":val(r,"notice_id","id","ted_id"),
            "title":val(r,"title","name"),"description":val(r,"description","text","summary"),
            "cpv":val(r,"cpv","cpv_code","classification"),
            "project_type_predicted":val(r,"project_type","type"),
            "trades_predicted":"; ".join(map(str,arr(val(r,"trades","trade","classified_trades",default=[])))),
            "confidence":e["confidence"],"quality_status":x["status"],
            "evidence":json.dumps(e,ensure_ascii=False),
            "project_type_correct":"","trades_correct":"","false_positive":"","review_notes":""
        })

summary={
 "version":"0.8.5","source":source,"records_seen":len(records),
 "records_evaluated":len(evaluated),"quality_gate":dict(counts),
 "customer_facing_confident":counts.get("CONFIDENT",0),
 "held_for_review":counts.get("REVIEW",0),"suppressed_unknown":counts.get("UNKNOWN",0),
 "audit_sample_size":len(sample),"gate_total_check":sum(counts.values()),
 "gate_total_matches_records":sum(counts.values())==len(evaluated),
 "accuracy_measured":False,
 "accuracy_note":"Quality gate is evidence screening, not measured precision. Review labels are required for accuracy."
}
(REPORTS/"quality_validation_summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
(DOCS/"quality_validation.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(summary,ensure_ascii=False,indent=2))
if len(records)<100:
    raise SystemExit("Full-dataset gate refused website-feed-sized input (<100 records).")
