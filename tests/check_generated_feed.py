"""End-to-end assertions against the complete committed data, run by CI."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from intelligence.evidence import classify_evidence
def read(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))
live=read("real_data/ted_live_normalized.json")
enriched=read("real_data/ted_live_enriched.json")
feed=read("docs/data/customer_opportunities.json")
customer=read("docs/data/bauradar_feed.json")
status=read("docs/data/status.json")
assert len(enriched)==status["quality_records"] and len(enriched)<=len(live)
assert len({r["source_id"] for r in enriched})==len(enriched)
assert feed["count"]==len(feed["opportunities"])==status["quality_confident"]
assert all(classify_evidence(r)[0]=="CONFIDENT" for r in feed["opportunities"])
assert customer["count"]==len(customer["opportunities"])==status["opportunities"]
assert all(r["quality_status"] in ("CONFIDENT","VERIFIED_EARLY") for r in customer["opportunities"])
assert len({r["id"] for r in customer["opportunities"]})==customer["count"], "Duplicate customer identity"
assert all(r["expected_tender_period"] is None for r in customer["opportunities"])
assert status["early_signals"]==len(read("real_data/bavaria_verified_events.json"))
print(json.dumps({"verified":True,"source_records":len(live),"customer_ted":feed["count"],
    "early_signals":status["early_signals"],"master_projects":status["master_projects"],
    "lifecycle_candidates":status["lifecycle_candidates"],"confirmed_links":status["lifecycle_links"]}))
