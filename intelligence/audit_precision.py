from __future__ import annotations
import csv, json, random, re
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
REAL=ROOT/'real_data'; REPORTS=ROOT/'reports'; DOCS=ROOT/'docs'/'data'
REPORTS.mkdir(exist_ok=True); DOCS.mkdir(parents=True,exist_ok=True)

def load(p, default):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception:return default

def arr(v): return v if isinstance(v,list) else ([] if v in (None,'') else [v])
def score01(r):
    try:
        x=float(r.get('classification_confidence',0) or 0)
        return min(1,max(0,x/100 if x>1 else x))
    except Exception:return 0


# v0.8.9: make multilingual TED records readable for human audit without deleting source evidence.
EN_HINTS=("construction work", "building work", "works for", "renovation", "installation work", "engineering work", "road works", "railway", "pipeline", "electrical", "heating", "ventilation", "plumbing")
DE_HINTS=("bauarbeiten", "bauleistungen", "neubau", "sanierung", "umbau", "erweiterung", "elektro", "heizung", "lüftung", "rohrleitung", "straßenbau", "gleis", "brücke")
LANG_MARKER=re.compile(r"(?:^|\s)(?:Germany|Deutschland|Poland|Polen|France|Frankreich|Italy|Italien|Spain|Spanien|Austria|Österreich|Belgium|Belgien|Netherlands|Niederlande|Czechia|Tschechien|Sweden|Schweden|Denmark|Dänemark|Finland|Finnland|Romania|Rumänien|Hungary|Ungarn|Slovakia|Slowakei|Slovenia|Slowenien|Croatia|Kroatien|Bulgaria|Bulgarien|Greece|Griechenland|Portugal|Ireland|Irland|Lithuania|Litauen|Latvia|Lettland|Estonia|Estland)[-–—][^:]{1,80}:\s*",re.I)

def clean_space(v): return re.sub(r"\s+"," ",str(v or "")).strip()

def readable_ted_text(text):
    raw=clean_space(text)
    if not raw:return ""
    starts=[m.start() for m in LANG_MARKER.finditer(raw)]
    parts=[]
    if starts:
        starts.append(len(raw))
        parts=[raw[starts[i]:starts[i+1]].strip(" ;|") for i in range(len(starts)-1)]
    else: parts=[raw]
    def rank(x):
        z=x.lower(); en=sum(k in z for k in EN_HINTS); de=sum(k in z for k in DE_HINTS)
        # Prefer concise German, then English, and strongly penalize giant multilingual blocks.
        return (3 if de else 0)+(2 if en else 0)-max(0,len(x)-420)/300
    best=max(parts,key=rank) if parts else raw
    best=LANG_MARKER.sub("",best,count=1).strip(" ;|")
    if len(best)>700: best=best[:697].rsplit(" ",1)[0]+"…"
    return best or raw[:700]

def evidence_excerpt(text, max_len=430):
    """Return one compact German/English evidence excerpt from multilingual TED text."""
    raw=clean_space(text)
    if not raw:return ""
    low=raw.lower()
    hints=list(DE_HINTS)+list(EN_HINTS)
    hits=[low.find(h) for h in hints if low.find(h)>=0]
    if not hits:
        return (raw[:max_len-1].rsplit(" ",1)[0]+"…") if len(raw)>max_len else raw
    pos=min(hits)
    # Start after the nearest language/country label colon when possible.
    left=max(0,pos-150)
    colon=raw.rfind(":",left,pos)
    begin=colon+1 if colon>=0 else left
    # Stop before the next obvious language/country label.
    tail=raw[pos+40:]
    m=LANG_MARKER.search(tail)
    finish=pos+40+(m.start() if m else max_len)
    excerpt=clean_space(raw[begin:min(len(raw),finish)]).strip(" ;|:-")
    if len(excerpt)>max_len:
        excerpt=excerpt[:max_len-1].rsplit(" ",1)[0]+"…"
    return excerpt

def compact_audit_card(r):
    title=evidence_excerpt(r.get('title'),360)
    desc=evidence_excerpt(r.get('description'),430)
    if desc==title: desc=""
    return title,desc

def audit_summary(r):
    return compact_audit_card(r)

import sys
sys.path.insert(0, str(ROOT))
from intelligence.evidence import classify_evidence as evidence_gate

records=load(REAL/'ted_live_enriched.json',[])
if not isinstance(records,list) or len(records)<100: raise SystemExit('Audit layer requires >=100 enriched records.')
rows=[]
for r in records:
    if not isinstance(r,dict): continue
    status,e=evidence_gate(r); rows.append({'record':r,'quality_status':status,'evidence':e})
counts=Counter(x['quality_status'] for x in rows)

# Customer feed contains only evidence-gated CONFIDENT records. No REVIEW/UNKNOWN leakage.
customer=[dict(x['record'], quality_status='CONFIDENT', quality_evidence=x['evidence']) for x in rows if x['quality_status']=='CONFIDENT']
customer.sort(key=lambda r:(float(r.get('score') or 0),str(r.get('published') or '')),reverse=True)
feed={'version':'0.8.9','policy':'CONFIDENT_ONLY','count':len(customer),'opportunities':customer}
(DOCS/'customer_opportunities.json').write_text(json.dumps(feed,ensure_ascii=False,indent=2),encoding='utf-8')

# Deterministic 60-case stratified audit pack. Labels remain blank until human review.
rng=random.Random(807); sample=[]
for status,n in [('CONFIDENT',25),('REVIEW',25),('UNKNOWN',10)]:
    bucket=[x for x in rows if x['quality_status']==status]; rng.shuffle(bucket); sample+=bucket[:n]
fields=['audit_id','notice_id','title','description','cpv','project_type_predicted','trades_predicted','confidence','quality_status','evidence_reason','project_type_correct','trades_correct','false_positive','review_notes']
with (REPORTS/'audit_v086.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for i,x in enumerate(sample,1):
        r=x['record']; e=x['evidence']; clean_title,clean_desc=audit_summary(r)
        reason=f"project={e['project_type']}; trade={e['trade']}; cpv={e['cpv']}; text={e['textual_evidence']}; confidence={e['confidence']}"
        w.writerow({'audit_id':i,'notice_id':r.get('notice_id'),'title':clean_title,'description':clean_desc,'cpv':'; '.join(map(str,arr(r.get('cpv')))),'project_type_predicted':r.get('project_type'),'trades_predicted':'; '.join(map(str,arr(r.get('trades')))),'confidence':e['confidence'],'quality_status':x['quality_status'],'evidence_reason':reason,'project_type_correct':'','trades_correct':'','false_positive':'','review_notes':''})

# Browser-readable audit pack for the GitHub Pages Quality Audit UI.
audit_cases=[]
for i,x in enumerate(sample,1):
    r=x['record']; e=x['evidence']; clean_title,clean_desc=audit_summary(r)
    audit_cases.append({
        'audit_id':i,'notice_id':r.get('notice_id'),'title':clean_title,
        'description':clean_desc,'original_title':r.get('title'),'original_description':r.get('description'),'cpv':arr(r.get('cpv')),
        'project_type_predicted':r.get('project_type'),'trades_predicted':arr(r.get('trades')),
        'confidence':e['confidence'],'quality_status':x['quality_status'],
        'evidence':e,'authority':r.get('authority'),'published':r.get('published'),'city':r.get('city'),
        'country':r.get('country'),'source_url':r.get('source_url'),'phase':r.get('phase')
    })
(DOCS/'audit_cases.json').write_text(json.dumps({'version':'0.8.9','count':len(audit_cases),'cases':audit_cases},ensure_ascii=False,indent=2),encoding='utf-8')

# Precision is calculated only when a reviewed audit CSV exists; never fabricated.
labels=REPORTS/'audit_v086_reviewed.csv'; metrics={'measured':False,'reviewed_rows':0,'precision':None,'project_type_accuracy':None,'trade_accuracy':None}
if labels.exists():
    with labels.open(encoding='utf-8-sig',newline='') as f: reviewed=list(csv.DictReader(f))
    def yes(v): return str(v).strip().lower() in ('1','true','yes','ja','y')
    labelled=[r for r in reviewed if str(r.get('false_positive','')).strip()!='']
    if labelled:
        metrics['measured']=True; metrics['reviewed_rows']=len(labelled)
        metrics['precision']=round(100*sum(not yes(r.get('false_positive')) for r in labelled)/len(labelled),1)
        pt=[r for r in labelled if str(r.get('project_type_correct','')).strip()!='']
        tr=[r for r in labelled if str(r.get('trades_correct','')).strip()!='']
        metrics['project_type_accuracy']=round(100*sum(yes(r.get('project_type_correct')) for r in pt)/len(pt),1) if pt else None
        metrics['trade_accuracy']=round(100*sum(yes(r.get('trades_correct')) for r in tr)/len(tr),1) if tr else None
summary={'version':'0.8.9','records_evaluated':len(rows),'quality_gate':dict(counts),'customer_feed_count':len(customer),'customer_feed_policy':'CONFIDENT_ONLY','review_leakage':sum(1 for r in customer if r.get('quality_status')!='CONFIDENT'),'audit_sample_size':len(sample),'accuracy':metrics,'accuracy_note':'Precision is reported only from explicitly reviewed labels; otherwise it remains unmeasured.'}
(REPORTS/'audit_precision_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(DOCS/'audit_precision.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
if summary['review_leakage']!=0: raise SystemExit('Customer feed policy violation.')
