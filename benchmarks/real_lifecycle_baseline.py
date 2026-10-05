import os,sys,json
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,ROOT);sys.path.insert(0,os.path.join(ROOT,"lifecycle"))
from graph import lifecycle_status
events=json.load(open(os.path.join(ROOT,"real_data","bavaria_verified_events.json"),encoding="utf-8"))
# At v0.6 baseline these verified records are early funding signals; later DÖE/TED events
# are what must close the lifecycle.
projects={}
for e in events:
    k=(e["city"],e["title"])
    projects.setdefault(k,[]).append(e["phase"])
stats=[lifecycle_status(v) for v in projects.values()]
print(json.dumps({"verified_early_event_records":len(events),
 "baseline_project_keys":len(projects),
 "with_early":sum(x["has_early"] for x in stats),
 "with_planning":sum(x["has_planning"] for x in stats),
 "with_tender":sum(x["has_tender"] for x in stats),
 "with_award":sum(x["has_award"] for x in stats),
 "note":"No later events are fabricated; live procurement enrichment is required to close these chains."},indent=2))
