import os,sys,json
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,ROOT)
from engine import SourceEvent, Project, project_similarity

def P(name,city,typ):
    return Project("X",name,city,"Bayern","DE",typ,"funding",50)
def E(title,city,typ):
    return SourceEvent("s","x","u","2026-01-01",title,"",city=city,region="Bayern",project_type=typ,phase="funding")

pairs=[
 (P("Neubau Grundschule mit Sporthalle","Gammelsdorf","school"),E("Neubau einer Grundschule mit Sporthalle","Gammelsdorf","school"),1),
 (P("Erweiterung Kindertageseinrichtung","Oberbergkirchen","kindergarten"),E("Erweiterung der Kindertageseinrichtung","Oberbergkirchen","kindergarten"),1),
 (P("Neubau Kindertageseinrichtung","Meeder","kindergarten"),E("Neubau Kindertageseinrichtung","Marktleuthen","kindergarten"),0),
 (P("Generalsanierung Gymnasium","Roth","school"),E("Generalsanierung Grundschule","Naila","school"),0),
]
tp=tn=fp=fn=0
for p,e,label in pairs:
    pred=project_similarity(p,e)>=.72
    if pred and label: tp+=1
    elif pred and not label: fp+=1
    elif not pred and label: fn+=1
    else: tn+=1
precision=tp/(tp+fp) if tp+fp else 0
recall=tp/(tp+fn) if tp+fn else 0
print(json.dumps({"pairs":len(pairs),"tp":tp,"tn":tn,"fp":fp,"fn":fn,
                  "precision":precision,"recall":recall},indent=2))
