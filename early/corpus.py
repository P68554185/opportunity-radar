"""Verified active events, separate from retrospective validation evidence."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def active_events():
    events=[]
    for name in ("bavaria_verified_events.json","early_verified_events.json","municipal_verified_events.json"):
        path=ROOT/"real_data"/name
        if path.exists():
            events.extend(json.loads(path.read_text(encoding="utf-8")))
    result={}
    for event in events:
        sid=event["source_id"]
        if sid in result and result[sid]!=event:
            raise ValueError("Conflicting EARLY source identity")
        result[sid]=event
    return list(result.values())
