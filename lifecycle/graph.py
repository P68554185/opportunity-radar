"""Lifecycle graph for v0.6: EARLY -> planning -> tender -> award."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime
from difflib import SequenceMatcher
import re, json

PHASE_ORDER={"project_announced":0,"prior_information":5,"idea":0,"political_decision":1,"funding":2,"object_planning":3,
             "specialist_planning":4,"execution_planning":5,"tender":6,"award":7}

def norm(s):
    return " ".join(re.sub(r"[^a-z0-9äöüß ]+"," ",(s or "").lower()).split())

def tokens(s):
    stop={"neubau","umbau","sanierung","generalsanierung","erweiterung","der","des","die",
          "und","mit","für","einer","eines","von","im","in"}
    return {x for x in norm(s).split() if len(x)>3 and x not in stop}

def jaccard(a,b):
    a,b=tokens(a),tokens(b)
    return len(a&b)/len(a|b) if a|b else 0

def link_score(project,event):
    # Known contradictory municipalities block automatic links.
    if project.city and event.city and norm(project.city)!=norm(event.city):
        return 0.0,{"city_contradiction":1}
    city=1 if project.city and event.city and norm(project.city)==norm(event.city) else 0
    typ=1 if project.project_type and event.project_type and project.project_type==event.project_type else 0
    title=SequenceMatcher(None,norm(project.canonical_name),norm(event.title)).ratio()
    token=jaccard(project.canonical_name,event.title)
    authority=SequenceMatcher(None,norm(getattr(project,"authority","")),norm(event.authority)).ratio() if event.authority else 0
    score=.34*city+.16*typ+.24*title+.21*token+.05*authority
    return round(score,4),{"city":city,"type":typ,"title":round(title,3),
                           "token":round(token,3),"authority":round(authority,3)}

def classify_link(score,best_gap=1):
    if score>=.82 and best_gap>=.08: return "auto_link"
    if score>=.64: return "review"
    return "unlinked"

def lifecycle_status(phases):
    phases=set(phases)
    return {
      "has_early":bool(phases & {"idea","political_decision","funding"}),
      "has_planning":bool(phases & {"object_planning","specialist_planning","execution_planning"}),
      "has_tender":"tender" in phases,
      "has_award":"award" in phases,
      "max_phase":max(phases,key=lambda p:PHASE_ORDER.get(p,-1)) if phases else None
    }
