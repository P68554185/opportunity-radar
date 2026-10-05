import os,sys,json,tempfile
ROOT=os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0,ROOT)
from bulk_runner import BulkRunner

def rec(i):
    city=f"Feedstadt {i}"
    return {"source_id":f"DOE-OFFICIAL-FEED-{i}","source_type":"doe_ocds_fixture",
      "source_url":"https://oeffentlichevergabe.de/ui/de/search",
      "published":"2026-01-01","title":f"Baumaßnahme Schulzentrum {i}",
      "body":"OCDS-normalized official-feed fixture","authority":f"Stadt {city}",
      "city":city,"region":"Bayern","country":"DE","project_type":"school","phase":"tender",
      "external_id":f"ocds-{i}"}
records=[rec(i) for i in range(625)]
with tempfile.TemporaryDirectory() as d:
    runner=BulkRunner(os.path.join(d,"bulk.sqlite"),os.path.join(d,"checkpoint.json"),250)
    projects,cp=runner.execute(records)
    db=__import__("sqlite3").connect(os.path.join(d,"bulk.sqlite"))
    raw=db.execute("select count(*) from raw_events").fetchone()[0]
    assert raw==625,raw
    assert cp["batches"]==3
    assert cp["records_processed"]==625
    print(json.dumps({"official_feed_format_records":625,"raw_events_persisted":raw,
      "batches":cp["batches"],"checkpoint_status":cp["status"]},indent=2))
