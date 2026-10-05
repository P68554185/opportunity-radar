import tempfile
import unittest
from pathlib import Path
from pipeline import run
from engine import SourceEvent, resolve_project

class PersistenceTests(unittest.TestCase):
    def test_incremental_runs_keep_history(self):
        with tempfile.TemporaryDirectory() as d:
            db=str(Path(d)/"test.sqlite")
            first=dict(source_id="a",source_type="official",source_url="https://example.org/a",
                published="2026-01-01",title="Neubau Grundschule Sonnenberg",body="",city="Roth",
                project_type="school",phase="funding")
            p=run([first],db)
            second=dict(first,source_id="b",source_url="https://example.org/b",phase="tender",published="2026-04-01")
            q=run([second],db)
            self.assertEqual(len(q),1); self.assertEqual(q[0].project_id,p[0].project_id)
            self.assertEqual(q[0].phase,"tender"); self.assertEqual(len(q[0].event_ids),2)
            self.assertEqual(len(run([second],db)[0].event_ids),2)

    def test_conflicting_project_types_do_not_merge(self):
        projects=[]
        base=dict(source_id="a",source_type="official",source_url="u",published="2026-01-01",
                  title="Neubau Hauptgebäude",body="",city="Roth",project_type="school")
        resolve_project(projects,SourceEvent(**base))
        resolve_project(projects,SourceEvent(**dict(base,source_id="b",project_type="hospital")))
        self.assertEqual(len(projects),2)

if __name__=="__main__": unittest.main()
