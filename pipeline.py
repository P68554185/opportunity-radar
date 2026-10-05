"""v0.3 pipeline runner: JSON or adapter records -> immutable events -> projects -> store."""
from engine import SourceEvent, event_key, resolve_project
from storage import DevStore

def run(records, db_path="engine_v03.sqlite"):
    store=DevStore(db_path)
    projects=store.load_projects()
    seen=set()
    for raw in records:
        e=SourceEvent(**raw)
        k=event_key(e)
        store.save_event(k, raw)
        if k in seen: continue
        seen.add(k)
        resolve_project(projects,e)
    for p in projects:
        store.save_project(p)
    return projects
