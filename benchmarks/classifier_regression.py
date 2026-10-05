import os,sys,json
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,"classification"))
from rules import classify
cases=[("Elektroarbeiten Generalsanierung Gymnasium Roth","school","electrical"),
("Lüftungs- und Sanitärarbeiten Kindergarten Sonnenhügel","kindergarten","hvac"),
("Rohbau Neubau Feuerwehrhaus","fire_station","structural"),("Malerarbeiten Klinikum","hospital","painting")]
details=[];ok=0
for txt,pt,tr in cases:
 a,b=classify(txt);passed=(a==pt and tr in b);ok+=passed;details.append([txt,a,b,passed])
assert ok==len(cases),details
print(json.dumps({"cases":len(cases),"passed":ok,"details":details},ensure_ascii=False,indent=2))
