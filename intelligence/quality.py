"""Quality analytics for live Opportunity Radar classifications."""
import json, os
from collections import Counter
ROOT=os.path.dirname(os.path.dirname(__file__))

def load(path, default):
    try:
        with open(path, encoding='utf-8') as f: return json.load(f)
    except Exception: return default

def pct(n,d): return round(100*n/d,1) if d else 0.0

def build_quality():
    intel=load(os.path.join(ROOT,'reports','intelligence_report.json'),{})
    live=load(os.path.join(ROOT,'real_data','ted_live_normalized.json'),[])
    opp=intel.get('opportunities',[])
    # intelligence_report stores top 50; derive full distributions directly from live records using same eligibility/score logic.
    from build import opportunity_score
    full=[]
    for x in live:
        if not (x.get('project_type') or x.get('_trades')): continue
        score=opportunity_score(x)
        band='HOT' if score>=85 else ('UPCOMING' if score>=65 else 'EARLY')
        full.append({**x,'score':score,'band':band})
    project=Counter(x.get('project_type') or 'unclassified_project' for x in full)
    trades=Counter(t for x in full for t in x.get('_trades',[]))
    bands=Counter(x['band'] for x in full)
    scores=Counter((x['score']//10)*10 for x in full)
    quality={
      'live_records':len(live),'classified_opportunities':len(full),'classification_rate_pct':pct(len(full),len(live)),
      'bands':dict(bands),'project_types':project.most_common(),'trades':trades.most_common(),
      'score_buckets':[{'from':k,'to':min(100,k+9),'count':scores[k]} for k in sorted(scores)],
      'quality_flags':{
        'project_type_only':sum(1 for x in full if x.get('project_type') and not x.get('_trades')),
        'trade_only':sum(1 for x in full if not x.get('project_type') and x.get('_trades')),
        'project_and_trade':sum(1 for x in full if x.get('project_type') and x.get('_trades')),
        'high_confidence_85_plus':sum(1 for x in full if x['score']>=85)
      },
      'sample_top':[{
        'source_id':x.get('source_id'),'title':x.get('title'),'authority':x.get('authority'),'city':x.get('city'),
        'project_type':x.get('project_type'),'trades':x.get('_trades',[]),'score':x['score'],'band':x['band'],
        'reason':('Projektart + Gewerke' if x.get('project_type') and x.get('_trades') else ('Projektart erkannt' if x.get('project_type') else 'Gewerk/CPV erkannt')),
        'source_url':x.get('source_url')
      } for x in sorted(full,key=lambda z:(z['score'],z.get('published') or ''),reverse=True)[:12]]
    }
    os.makedirs(os.path.join(ROOT,'docs','data'),exist_ok=True);os.makedirs(os.path.join(ROOT,'reports'),exist_ok=True)
    for p in [os.path.join(ROOT,'reports','quality_report.json'),os.path.join(ROOT,'docs','data','quality.json')]:
        with open(p,'w',encoding='utf-8') as f: json.dump(quality,f,ensure_ascii=False,indent=2)
    print(json.dumps({k:v for k,v in quality.items() if k not in ('sample_top','project_types','trades','score_buckets')},ensure_ascii=False,indent=2))
    return quality
if __name__=='__main__': build_quality()
