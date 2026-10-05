"""v0.4 entity resolution with explicit evidence and quarantine."""
from difflib import SequenceMatcher
import re

def norm(s):
    return " ".join(re.sub(r"[^a-z0-9äöüß ]+"," ",(s or "").lower()).split())

def score(project,event):
    # Hard contradiction: known different municipalities are not the same project.
    if project.city and event.city and norm(project.city)!=norm(event.city):
        return 0.0, {"city_contradiction":1.0}
    parts={}
    parts["city"]=1.0 if project.city and norm(project.city)==norm(event.city) else 0.0
    parts["type"]=1.0 if project.project_type and project.project_type==event.project_type else 0.0
    parts["title"]=SequenceMatcher(None,norm(project.canonical_name),norm(event.title)).ratio()
    parts["authority"]=SequenceMatcher(None,norm(getattr(project,"authority","")),
                                       norm(event.authority)).ratio() if event.authority else 0.0
    total=.42*parts["city"]+.23*parts["type"]+.30*parts["title"]+.05*parts["authority"]
    return round(total,4),parts

def decision(best,second=None):
    # Ambiguous near-ties are quarantined instead of auto-merging.
    if best < .68: return "new"
    if second is not None and best-second < .07: return "quarantine"
    if best >= .78: return "merge"
    return "review"
