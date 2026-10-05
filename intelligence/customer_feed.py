"""Customer presentation feed; evidence policy and procurement lifecycle stay separate."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from engine import ingest, ONTOLOGY
from intelligence.evidence import POLICY_VERSION

def next_action(phase):
    if phase=="tender":return "Vergabeunterlagen und Frist in der Originalquelle prüfen."
    if phase=="award":return "Zuschlag und Auftragnehmer in der Originalquelle prüfen."
    if phase=="prior_information":return "Geplante Lose und den vorgesehenen Vergabezeitpunkt in der Vorankündigung prüfen."
    return "Projektphase und nächsten Vergabeschritt beim Auftraggeber oder in der Originalquelle klären."

def build():
    data=ROOT/"docs"/"data"
    tender=json.loads((data/"customer_opportunities.json").read_text(encoding="utf-8"))
    early=json.loads((ROOT/"real_data"/"bavaria_verified_events.json").read_text(encoding="utf-8"))
    registry=json.loads((ROOT/"real_data"/"source_registry.json").read_text(encoding="utf-8"))
    official={r["source_url"] for r in registry if r.get("status")=="official_verified"}
    projects=ingest(early)
    records=[]
    for r in tender["opportunities"]:
        if r.get("quality_status")!="CONFIDENT": raise ValueError("Feed quality violation")
        records.append(dict(r, id=r["source_id"], trade_basis="notice",
            expected_tender_period=None,
            next_action=next_action(r.get("phase"))))
    for p in projects:
        evidence=[r for r in early if r["source_url"] in official and r["city"]==p.city and r["title"]==p.canonical_name]
        if not evidence: continue
        r=max(evidence,key=lambda x:x["published"])
        records.append({"id":p.project_id,"source_id":r["source_id"],"title":p.canonical_name,
            "city":p.city,"region":p.region,"country":p.country,"authority":r.get("authority"),
            "published":r["published"],"phase":p.phase,"project_type":p.project_type,
            "trades":list(ONTOLOGY.get(p.project_type,{})), "trade_basis":"project_type_expected",
            "source_url":r["source_url"],"quality_status":"VERIFIED_EARLY",
            "opportunity_score":None,"expected_tender_period":None,
            "next_action":"Bauvorhaben beim Auftraggeber prüfen und nach dem geplanten Vergabezeitpunkt fragen."})
    out={"policy_version":POLICY_VERSION,"count":len(records),"opportunities":records,
        "notes":{"expected_trades":"Bei frühen Projekten aus der Projektart abgeleitet, noch keine bestätigten Lose.",
                 "dates":"Unbekannte Vergabezeiträume bleiben leer."}}
    (data/"bauradar_feed.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    report={"early_signals":len(early),"master_projects":len(projects),
            "verified_early_projects":sum(r["quality_status"]=="VERIFIED_EARLY" for r in records),
            "customer_ted_records":len(tender["opportunities"]),"customer_records":len(records)}
    (ROOT/"reports"/"customer_feed_summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report))
    return out

if __name__=="__main__": build()
