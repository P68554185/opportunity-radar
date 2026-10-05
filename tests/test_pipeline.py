import json, tempfile, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pipeline import run
from storage import DevStore

base=os.path.dirname(os.path.dirname(__file__))
events=json.load(open(os.path.join(base,"sample_events.json"),encoding="utf-8"))
with tempfile.TemporaryDirectory() as d:
    db=os.path.join(d,"test.sqlite")
    projects=run(events,db)
    assert len(projects)==3
    s=DevStore(db)
    assert s.db.execute("select count(*) from raw_events").fetchone()[0]==3
    assert s.db.execute("select count(*) from projects").fetchone()[0]==3
print("v0.3 smoke test OK")
