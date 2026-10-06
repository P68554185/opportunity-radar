"""Reject incomplete or oversized growth snapshots before committing public data."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from live.settings import volume
target,_=volume()
report=json.loads((ROOT/"reports/live_ted_500_report.json").read_text())
rows=json.loads((ROOT/"real_data/ted_live_normalized.json").read_text())
feed=json.loads((ROOT/"docs/data/bauradar_feed.json").read_text())
assert report["status"]=="complete" and not report["errors"]
assert report["requested"]==len(rows)==target
assert len({r["source_id"] for r in rows})==target
assert feed["count"]==len(feed["opportunities"])
feed_bytes=(ROOT/"docs/data/bauradar_feed.json").stat().st_size
assert feed_bytes<=12_000_000,"Customer feed exceeds the production cache limit; partition before growing further"
for path in list((ROOT/"docs/data").glob("*.json"))+list((ROOT/"real_data").glob("*.json")):
    assert path.stat().st_size<80_000_000,"Public snapshot blob exceeds operational growth budget"
result={"target":target,"verified_source_records":len(rows),"customer_records":feed["count"],"customer_feed_bytes":feed_bytes,
    "maximum_customer_feed_bytes":12_000_000,"no_accuracy_claim":True,"verified":True}
(ROOT/"reports/data_growth_acceptance.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps(result))
