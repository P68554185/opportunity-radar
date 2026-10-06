"""Status is derived from current generated datasets, never hard-coded totals."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def load(path,default):
    try: return json.loads((ROOT/path).read_text(encoding="utf-8"))
    except FileNotFoundError: return default
def build():
    live=load("real_data/ted_live_normalized.json",[])
    report=load("reports/live_ted_500_report.json",{})
    intel=load("reports/intelligence_report.json",{})
    lifecycle=load("reports/lifecycle_report.json",{})
    historical=load("reports/historical_lifecycle_validation.json",{})
    gate=load("reports/quality_validation_summary.json",{})
    customer=load("reports/customer_feed_summary.json",{})
    dates=sorted(str(x["published"])[:10] for x in live if x.get("published"))
    classified=intel.get("classified_opportunities",0)
    status={"version":"0.10.0","early_signals":customer.get("early_signals",0),
        "master_projects":customer.get("master_projects",0),"live_records":len(live),
        "classified_opportunities":classified,
        "classification_rate_pct":round(100*classified/len(live),1) if live else 0,
        "opportunities":customer.get("customer_records",0),
        "customer_ted_records":customer.get("customer_ted_records",0),
        "located_projects":customer.get("located_projects",0),
        "dresden_early_projects":customer.get("dresden_early_projects",0),
        "lifecycle_candidates":lifecycle.get("candidate_notice_links",0),
        "lifecycle_links":lifecycle.get("confirmed_current_notice_links",0),
        "lifecycle_links_including_history":lifecycle.get("confirmed_notice_links",0),
        "lifecycle_confirmed_projects":lifecycle.get("confirmed_project_cases",0),
        "historical_confirmed_projects":historical.get("confirmed_project_cases",0),
        "live_early_lead_measured":bool(lifecycle.get("live_observed_lead_days")),
        "last_sync":report.get("run_at"),"ted_run_status":report.get("status","never"),
        "ted_errors":len(report.get("errors",[])),"ted_requested":report.get("requested",0),
        "quality_confident":gate.get("customer_facing_confident",0),
        "quality_review":gate.get("held_for_review",0),"quality_unknown":gate.get("suppressed_unknown",0),
        "quality_records":gate.get("records_evaluated",0),"accuracy_measured":False,
        "data_from":dates[0] if dates else None,"data_to":dates[-1] if dates else None,
        "market":"Germany","ted_query":"RC = DEU AND classification-cpv = 45*; newest first"}
    (ROOT/"docs"/"data"/"status.json").write_text(json.dumps(status,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(status,ensure_ascii=False,indent=2))
    return status
if __name__=="__main__": build()
