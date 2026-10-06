"""Match verified source events to qualified procurement records, grouped by master."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from early.corpus import active_events
from engine import ingest, SourceEvent, event_key
from lifecycle.matching import evaluate, history, VERSION
from lifecycle.journal import observe,tracked_lead,preserve_confirmed
from intelligence.evidence import POLICY_VERSION

def build():
    active=active_events()
    historical=json.loads((ROOT/"real_data/historical_early_events.json").read_text())
    events=active+historical
    masters=ingest(events)
    memberships={key:p.project_id for p in masters for key in p.event_ids}
    current=json.loads((ROOT/"docs/data/customer_opportunities.json").read_text())["opportunities"]
    observation_path=ROOT/"real_data/early_observations.json"
    archive_path=ROOT/"real_data/lifecycle_notice_archive.json"
    observations=observe(json.loads(observation_path.read_text()) if observation_path.exists() else {},events)
    archive=json.loads(archive_path.read_text()) if archive_path.exists() else {}
    merged={sid:item["notice"] for sid,item in archive.items() if item.get("quality_policy_version")==POLICY_VERSION}
    merged.update({notice["source_id"]:notice for notice in current})
    notices=list(merged.values())
    pairs=[]
    for early in events:
        for notice in notices:
            if early.get("city")!=notice.get("city"): continue
            result=evaluate(early,notice)
            if result["status"]!="unlinked":
                pairs.append(dict(result,master_project_id=memberships[event_key(SourceEvent(**early))],
                    retrospective=early in historical))
    identities={}
    for pair in pairs:
        if pair["status"]=="confirmed":
            identities.setdefault(pair["source_ids"][1],set()).add(pair["master_project_id"])
    for pair in pairs:
        if len(identities.get(pair["source_ids"][1],set()))>1:
            pair["status"]="unlinked"
            pair["blockers"].append("ambiguous_master_identity")
    confirmed=[p for p in pairs if p["status"]=="confirmed"]
    preserve_confirmed(archive,current,confirmed)
    observation_path.write_text(json.dumps(observations,ensure_ascii=False,indent=2)+"\n")
    archive_path.write_text(json.dumps(archive,ensure_ascii=False,indent=2)+"\n")
    timelines=[]
    for master in masters:
        links=[p for p in confirmed if p["master_project_id"]==master.project_id]
        if not links: continue
        early_ids={p["source_ids"][0] for p in links}
        later_ids={p["source_ids"][1] for p in links}
        timelines.append({"master_project_id":master.project_id,"title":master.canonical_name,
            "history":history([e for e in events if e["source_id"] in early_ids]+
                              [n for n in notices if n["source_id"] in later_ids])})
    report={"matching_version":VERSION,"active_early_signals":len(active),
        "active_master_projects":len(ingest(active)),"historical_signals":len(historical),
        "qualified_procurement_records":len(current),
        "archived_confirmed_notices":len(archive),"links":pairs,"timelines":timelines,
        "confirmed_notice_links":len(confirmed),
        "confirmed_project_cases":len(timelines),
        "candidate_notice_links":sum(p["status"] in ("candidate","probable") for p in pairs),
        "live_observed_lead_days":[{"source_ids":p["source_ids"],"days":lead}
            for p in confirmed
            for lead in [tracked_lead(observations[p["source_ids"][0]],
                next(n for n in notices if n["source_id"]==p["source_ids"][1]))] if lead is not None],
        "observed_lead_note":"Tracked observation to this notice; not necessarily the project's first tender.",
        "note":"Retrospective source dates do not demonstrate prospective BauRadar lead or first tender."}
    (ROOT/"reports/lifecycle_report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("active_early_signals","active_master_projects",
        "qualified_procurement_records","confirmed_notice_links","confirmed_project_cases","candidate_notice_links")}))
    return report
if __name__=="__main__": build()
