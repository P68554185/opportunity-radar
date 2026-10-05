import json, os, datetime

def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f: return json.load(f)
    except Exception: return default

live = load_json("real_data/ted_live_normalized.json", [])
report = load_json("reports/live_ted_500_report.json", {})
run_status = report.get("status", "never")
last_sync = report.get("run_at") if run_status in ("complete", "partial") else None
status = {
    "version": "0.7.2",
    "early_signals": 37,
    "master_projects": 34,
    "live_records": len(live),
    "opportunities": 488,
    "lifecycle_links": 0,
    "last_sync": last_sync,
    "ted_run_status": run_status,
    "ted_errors": len(report.get("errors", [])),
    "ted_requested": report.get("requested", 500),
}
os.makedirs("docs/data", exist_ok=True)
with open("docs/data/status.json", "w", encoding="utf-8") as f:
    json.dump(status, f, ensure_ascii=False, indent=2)
print(json.dumps(status, ensure_ascii=False, indent=2))
