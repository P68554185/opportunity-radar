from __future__ import annotations
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'docs'/'data'; REPORTS=ROOT/'reports'
DATA.mkdir(parents=True,exist_ok=True); REPORTS.mkdir(exist_ok=True)

def load(p,default):
    try:return json.loads(p.read_text(encoding='utf-8'))
    except Exception:return default

def text(c): return ' '.join(str(c.get(k) or '') for k in ('title','description','original_title','original_description')).lower()
PROJECT_HINTS={
 'rail':('railway','railways','rail ','track','gleis','bahn','schiene'),
 'road':('road','roads','highway','motorway','straße','strasse','autobahn','fahrbahn'),
 'bridge':('bridge','brücke','viaduct'),
 'water_wastewater':('sewer','wastewater','water treatment','kanal','kläranlage','abwasser','wasserleitung'),
 'school':('school','schule','gymnasium','grundschule'),
 'fire_station':('fire station','feuerwehr','fire brigade'),
 'hospital':('hospital','clinic','krankenhaus','klinik'),
 'residential':('housing','residential','wohnungsbau','wohnungen'),
 'energy':('photovoltaic','solar','substation','power plant','energie','umspannwerk'),
 'admin':('town hall','city hall','rathaus','administration building','verwaltungsgebäude'),
}
TRADE_HINTS={
 'electrical':('electrical','electric','power line','strom','elektro','kabel'),
 'plumbing':('plumbing','pipeline','pipe','water line','rohr','sanitär','wasserleitung'),
 'railworks':('railway','track','gleis','schiene'),
 'structural':('concrete','steel structure','structural','stahlbeton','tragwerk'),
 'earthworks':('earthwork','excavation','groundwork','erdarbeiten','tiefbau','flatwork'),
 'hvac':('heating','ventilation','air conditioning','heizung','lüftung','klima'),
 'facade':('facade','fassade'),
 'roof':('roof','dach'),
 'windows_doors':('window','door','fenster','tür'),
}

def matches(t,hints): return sum(1 for h in hints if h in t)
def analyze(c):
    t=text(c); pred=str(c.get('project_type_predicted') or '').lower(); trades=[str(x).lower() for x in c.get('trades_predicted',[])]
    project_scores={k:matches(t,v) for k,v in PROJECT_HINTS.items()}; project_scores={k:v for k,v in project_scores.items() if v}
    best=sorted(project_scores.items(),key=lambda x:(-x[1],x[0]))
    predicted_support=project_scores.get(pred,0)
    alternatives=[k for k,v in best if k!=pred and v>=max(1,predicted_support)][:3]
    trade_support={tr:matches(t,TRADE_HINTS.get(tr,(tr,))) for tr in trades}
    unsupported=[tr for tr,v in trade_support.items() if v==0]
    broad=len([k for k,v in project_scores.items() if v>0])>=3
    reasons=[]; severity=0
    if pred and predicted_support==0: reasons.append('Projektart hat im Text keinen klaren Schlüsselwort-Beleg'); severity+=3
    if alternatives: reasons.append('Text stützt alternative Projektarten: '+', '.join(alternatives)); severity+=2
    if unsupported: reasons.append('Gewerke ohne direkten Textbeleg: '+', '.join(unsupported)); severity+=2
    if broad: reasons.append('Sehr breite/generische Leistungsbeschreibung – Überklassifizierung möglich'); severity+=2
    if float(c.get('confidence') or 0)>=.8 and severity>=4: reasons.append('Hohe Confidence trotz widersprüchlicher/breiter Evidenz'); severity+=1
    status='HIGH' if severity>=5 else ('MEDIUM' if severity>=2 else 'LOW')
    return dict(c, smart_review={'risk':status,'risk_score':severity,'reasons':reasons or ['Keine offensichtliche Regel-Kollision erkannt'],
      'project_text_support':predicted_support,'project_alternatives':alternatives,'trade_support':trade_support,'unsupported_trades':unsupported})

pack=load(DATA/'audit_cases.json',{'cases':[]}); cases=[analyze(c) for c in pack.get('cases',[])]
# Put suspicious cases first so human review has maximum information gain.
cases.sort(key=lambda c:(-c['smart_review']['risk_score'], {'UNKNOWN':0,'REVIEW':1,'CONFIDENT':2}.get(c.get('quality_status'),3), c.get('audit_id',999)))
for i,c in enumerate(cases,1): c['review_order']=i
out={'version':'0.9.0','count':len(cases),'strategy':'RISK_FIRST_ACTIVE_VALIDATION','cases':cases}
(DATA/'smart_audit_cases.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
summary={'version':'0.9.0','cases':len(cases),'risk':{k:sum(c['smart_review']['risk']==k for c in cases) for k in ('HIGH','MEDIUM','LOW')},'strategy':'Review highest-risk contradictions first; do not infer measured precision from unreviewed cases.'}
(REPORTS/'smart_validation_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
