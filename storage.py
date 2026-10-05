"""SQLite dev persistence. Production schema is in sql/postgres.sql."""
import sqlite3, json
from dataclasses import asdict

class DevStore:
    def __init__(self, path="engine_v03.sqlite"):
        self.db=sqlite3.connect(path)
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS raw_events(
          event_key TEXT PRIMARY KEY, source_id TEXT, source_type TEXT, source_url TEXT,
          published TEXT, payload_json TEXT NOT NULL, ingested_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS projects(
          project_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL, updated_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS project_events(
          project_id TEXT NOT NULL, event_key TEXT NOT NULL,
          PRIMARY KEY(project_id,event_key));
        """)
        self.db.commit()

    def save_event(self, event_key, event):
        self.db.execute("""INSERT OR IGNORE INTO raw_events
        (event_key,source_id,source_type,source_url,published,payload_json)
        VALUES(?,?,?,?,?,?)""",(event_key,event["source_id"],event["source_type"],
        event["source_url"],event["published"],json.dumps(event,ensure_ascii=False)))
        self.db.commit()

    def save_project(self, project):
        payload=json.dumps(asdict(project),ensure_ascii=False)
        self.db.execute("""INSERT INTO projects(project_id,payload_json) VALUES(?,?)
        ON CONFLICT(project_id) DO UPDATE SET payload_json=excluded.payload_json,
        updated_at=CURRENT_TIMESTAMP""",(project.project_id,payload))
        for ek in project.event_ids:
            self.db.execute("INSERT OR IGNORE INTO project_events(project_id,event_key) VALUES(?,?)",
                            (project.project_id,ek))
        self.db.commit()
