from __future__ import annotations
import csv, json, random
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
        x=float(r.get('confidence',r.get('score',0)) or 0)
        return min(1,max(0,x/100 if x>1 else x))
    except Exception:return 0

def evidence_gate(r):
    p=str(r.get('project_type') or '').lower()
    trades=arr(r.get('trades'))
    cpv=arr(r.get('cpv'))
    title=str(r.get('title') or '')
    desc=str(r.get('description') or '')
    project_ok=bool(p and p not in ('unknown','other','none'))
    trade_ok=bool(trades); cpv_ok=bool(cpv)
    textual=int(len(title)>=10)+int(len(desc)>=40)
    conf=score01(r)
    if project_ok and trade_ok and cpv_ok and textual>=1 and conf>=.70: status='CONFIDENT'
    elif (project_ok and trade_ok) or ((project_ok or trade_ok) and cpv_ok): status='REVIEW'
    else: status='UNKNOWN'
    return status, {'project_type':project_ok,'trade':trade_ok,'cpv':cpv_ok,'textual_evidence':textual,'confidence':round(conf,3)}

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
feed={'version':'0.8.6','policy':'CONFIDENT_ONLY','count':len(customer),'opportunities':customer}
(DOCS/'customer_opportunities.json').write_text(json.dumps(feed,ensure_ascii=False,indent=2),encoding='utf-8')

# Deterministic 60-case stratified audit pack. Labels remain blank until human review.
rng=random.Random(806); sample=[]
for status,n in [('CONFIDENT',25),('REVIEW',25),('UNKNOWN',10)]:
    bucket=[x for x in rows if x['quality_status']==status]; rng.shuffle(bucket); sample+=bucket[:n]
fields=['audit_id','notice_id','title','description','cpv','project_type_predicted','trades_predicted','confidence','quality_status','evidence_reason','project_type_correct','trades_correct','false_positive','review_notes']
with (REPORTS/'audit_v086.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
    for i,x in enumerate(sample,1):
        r=x['record']; e=x['evidence']
        reason=f"project={e['project_type']}; trade={e['trade']}; cpv={e['cpv']}; text={e['textual_evidence']}; confidence={e['confidence']}"
        w.writerow({'audit_id':i,'notice_id':r.get('notice_id'),'title':r.get('title'),'description':r.get('description'),'cpv':'; '.join(map(str,arr(r.get('cpv')))),'project_type_predicted':r.get('project_type'),'trades_predicted':'; '.join(map(str,arr(r.get('trades')))),'confidence':e['confidence'],'quality_status':x['quality_status'],'evidence_reason':reason,'project_type_correct':'','trades_correct':'','false_positive':'','review_notes':''})

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
summary={'version':'0.8.6','records_evaluated':len(rows),'quality_gate':dict(counts),'customer_feed_count':len(customer),'customer_feed_policy':'CONFIDENT_ONLY','review_leakage':sum(1 for r in customer if r.get('quality_status')!='CONFIDENT'),'audit_sample_size':len(sample),'accuracy':metrics,'accuracy_note':'Precision is reported only from explicitly reviewed labels; otherwise it remains unmeasured.'}
(REPORTS/'audit_precision_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(DOCS/'audit_precision.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
if summary['review_leakage']!=0: raise SystemExit('Customer feed policy violation.')
