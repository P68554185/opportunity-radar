"""Incremental v0.5 sync with checkpoints and provenance."""
import json, os
from pipeline import run

def load_json(path):
    with open(path,encoding="utf-8") as f: return json.load(f)

def sync_json(path, db_path, checkpoint_path):
    records=load_json(path)
    checkpoint={"input":path,"records_seen":len(records),"status":"started"}
    with open(checkpoint_path,"w",encoding="utf-8") as f: json.dump(checkpoint,f,indent=2)
    projects=run(records,db_path)
    checkpoint.update({"status":"complete","master_projects":len(projects)})
    with open(checkpoint_path,"w",encoding="utf-8") as f: json.dump(checkpoint,f,indent=2)
    return projects
