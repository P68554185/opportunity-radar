"""Offline historical audit against frozen, genuinely acquired TED notices."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from lifecycle.matching import evaluate, history, VERSION

def build():
    events=json.loads((ROOT/"real_data/historical_early_events.json").read_text())
    notices=json.loads((ROOT/"real_data/historical_procurement_notices.json").read_text())["notices"]
    comparisons=[]
    for event in events:
        for notice in notices:
            result=evaluate(event,notice)
            if result["evidence"]["same_city"]:
                comparisons.append(dict(result,early_url=event["source_url"],
                    later_url=notice["source_url"]))
    confirmed=[r for r in comparisons if r["status"]=="confirmed"]
    timelines=[]
    for event in events:
        linked=[n for n in notices if any(r["source_ids"]==[event["source_id"],n["source_id"]] for r in confirmed)]
        if linked:
            timelines.append({"early_source_id":event["source_id"],"history":history([event,*linked])})
    labelled_checks=[]
    for event in events:
        for notice in notices:
            if event["city"]!=notice["city"]:
                labelled_checks.append({"source_ids":[event["source_id"],notice["source_id"]],
                    "expected":"unlinked","actual":evaluate(event,notice)["status"],
                    "label_reason":"Different known project municipality"})
            elif event["city"]=="Alsfeld":
                labelled_checks.append({"source_ids":[event["source_id"],notice["source_id"]],
                    "expected":"confirmed","actual":evaluate(event,notice)["status"],
                    "label_reason":"Same explicitly named new hospital and identical legal owner, primary-source review"})
    report={"matching_version":VERSION,"historical_early_records":len(events),
        "frozen_procurement_records":len(notices),"comparisons":comparisons,
        "confirmed_notice_links":len(confirmed),
        "confirmed_project_cases":len(timelines),"timelines":timelines,
        "labelled_checks":labelled_checks,
        "labelled_positive_notice_pairs":sum(c["expected"]=="confirmed" for c in labelled_checks),
        "labelled_negative_notice_pairs":sum(c["expected"]=="unlinked" for c in labelled_checks),
        "missed_known_positive_pairs":sum(c["expected"]=="confirmed" and c["actual"]!="confirmed" for c in labelled_checks),
        "false_confirmations_in_labelled_negatives":sum(c["expected"]=="unlinked" and c["actual"]=="confirmed" for c in labelled_checks),
        "accuracy":None,"precision":None,"recall":None,
        "limitations":[
            "Purposefully selected retrospective examples; no representative labelled denominator.",
            "Early publication dates predate acquisition by BauRadar; no observed live detection lead.",
            "Intervals end at selected notices, not necessarily the first tender for a project.",
            "Tender and award intervals must not be combined into a first-tender lead statistic.",
            "Warburg issuer and buyer differ; a probable name match is not automatically confirmed.",
            "TH Koeln event date is not proven webpage publication date; interval withheld.",
            "Frozen TED facts come from the actual acquisition pipeline; subsequent corrections are not tracked here."]}
    (ROOT/"reports/historical_lifecycle_validation.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ["historical_early_records","frozen_procurement_records","confirmed_notice_links","confirmed_project_cases"]}))
    return report
if __name__=="__main__": build()
