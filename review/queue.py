"""SQLite review queue for ambiguous entity/lifecycle links."""
import sqlite3,json
class ReviewQueue:
    def __init__(self,path="review.sqlite"):
        self.db=sqlite3.connect(path)
        self.db.execute("""create table if not exists review_queue(
          id integer primary key autoincrement,
          project_id text,event_key text,score real,evidence_json text,status text default 'open',
          created_at text default current_timestamp,
          unique(project_id,event_key))"""); self.db.commit()
    def add(self,project_id,event_key,score,evidence):
        self.db.execute("""insert or ignore into review_queue(project_id,event_key,score,evidence_json)
          values(?,?,?,?)""",(project_id,event_key,score,json.dumps(evidence,ensure_ascii=False)))
        self.db.commit()
    def stats(self):
        return dict(self.db.execute("select status,count(*) from review_queue group by status").fetchall())
