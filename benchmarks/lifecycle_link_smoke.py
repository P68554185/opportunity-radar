import os,sys,json
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,ROOT); sys.path.insert(0,os.path.join(ROOT,"lifecycle"))
from engine import Project,SourceEvent
from graph import link_score,classify_link,lifecycle_status

def p(name,city,typ):
    return Project("P",name,city,"Bayern","DE",typ,"funding",50)
def e(title,city,typ,phase):
    return SourceEvent("s","doe","u","2026-01-01",title,"",city=city,region="Bayern",
                       project_type=typ,phase=phase)
cases=[
 (p("Generalsanierung Gymnasium Roth","Roth","school"),
  e("Elektroarbeiten Generalsanierung Gymnasium Roth","Roth","school","tender"),1),
 (p("Neubau Kindertageseinrichtung Sonnenhügel","Obernburg am Main","kindergarten"),
  e("HLS Neubau Kita Sonnenhügel","Obernburg am Main","kindergarten","tender"),1),
 (p("Erweiterung Gymnasium Kirchseeon","Kirchseeon","school"),
  e("Fachplanung TGA Erweiterung Gymnasium Kirchseeon","Kirchseeon","school","specialist_planning"),1),
 (p("Neubau Grundschule","Gammelsdorf","school"),
  e("Neubau Grundschule","Naila","school","tender"),0),
]
tp=tn=fp=fn=0; details=[]
for pr,ev,label in cases:
    sc,evidence=link_score(pr,ev); pred=sc>=.64
    details.append({"score":sc,"decision":classify_link(sc),"expected_link":bool(label)})
    if pred and label:tp+=1
    elif pred and not label:fp+=1
    elif not pred and label:fn+=1
    else:tn+=1
print(json.dumps({"cases":len(cases),"tp":tp,"tn":tn,"fp":fp,"fn":fn,
 "precision":tp/(tp+fp) if tp+fp else 0,"recall":tp/(tp+fn) if tp+fn else 0,
 "details":details},indent=2))
