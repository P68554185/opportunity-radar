"""Customer presentation feed; evidence policy and procurement lifecycle stay separate."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from engine import ingest, ONTOLOGY, event_key, SourceEvent
from early.corpus import active_events
from geography.dresden import locations
from lifecycle.matching import history
from intelligence.evidence import POLICY_VERSION

def next_action(phase):
    if phase=="tender":return "Vergabeunterlagen und Frist in der Originalquelle prüfen."
    if phase=="award":return "Zuschlag und Auftragnehmer in der Originalquelle prüfen."
    if phase=="prior_information":return "Geplante Lose und den vorgesehenen Vergabezeitpunkt in der Vorankündigung prüfen."
    return "Projektphase und nächsten Vergabeschritt beim Auftraggeber oder in der Originalquelle klären."

def collapse_confirmed(records,timelines):
    """Collapse only proven project identities, retaining legacy bookmark aliases."""
    by_id={r["id"]:r for r in records}
    removed=set(); merged=[]
    for timeline in timelines:
        notice_ids={e["source_id"] for e in timeline["history"] if e["source_id"].startswith("TED-")}
        ids=notice_ids|{timeline["master_project_id"]}
        rows=[by_id[key] for key in ids if key in by_id]
        notices=[r for r in rows if r["quality_status"]=="CONFIDENT"]
        if not notices: continue
        latest=max(notices,key=lambda r:(r.get("published") or "",r["source_id"]))
        phases={r.get("phase") for r in notices}
        merged.append(dict(latest,id=timeline["master_project_id"],
            master_project_id=timeline["master_project_id"],title=timeline["title"],
            aliases=sorted(ids-{timeline["master_project_id"]}),
            trades=sorted({trade for r in notices for trade in r["trades"]}),
            phase=latest["phase"] if len(phases)==1 else "procurement",
            project_history=timeline["history"],procurement_notice_count=len(notices),
            next_action="Die einzelnen Vergabemeldungen, passenden Gewerke und Fristen in den Originalquellen prüfen."))
        removed.update(r["id"] for r in rows)
    return [r for r in records if r["id"] not in removed]+merged

def build():
    data=ROOT/"docs"/"data"
    tender=json.loads((data/"customer_opportunities.json").read_text(encoding="utf-8"))
    early=active_events()
    registry=json.loads((ROOT/"real_data"/"source_registry.json").read_text(encoding="utf-8"))
    extra_registry=ROOT/"real_data"/"early_source_registry.json"
    if extra_registry.exists(): registry+=json.loads(extra_registry.read_text())
    official={r["source_url"] for r in registry if r.get("status")=="official_verified"}
    project_locations=locations(early)
    projects=ingest(early)
    records=[]
    historical_path=ROOT/"reports"/"lifecycle_report.json"
    historical=json.loads(historical_path.read_text()) if historical_path.exists() else {}
    confirmed_history={}
    for timeline in historical.get("timelines",[]):
        for event in timeline["history"]:
            if event["source_id"].startswith("TED-"):
                confirmed_history[event["source_id"]]=timeline["history"]
    for r in tender["opportunities"]:
        if r.get("quality_status")!="CONFIDENT": raise ValueError("Feed quality violation")
        records.append(dict(r, id=r["source_id"], trade_basis="notice",
            expected_tender_period=None,
            project_history=confirmed_history.get(r["source_id"],[]),
            next_action=next_action(r.get("phase"))))
    for p in projects:
        evidence=[r for r in early if r["source_url"] in official and event_key(SourceEvent(**r)) in p.event_ids]
        if not evidence: continue
        r=max(evidence,key=lambda x:x["published"])
        records.append({"id":p.project_id,"source_id":r["source_id"],"title":p.canonical_name,
            "city":p.city,"region":p.region,"country":p.country,"authority":r.get("authority"),
            "published":r["published"],"phase":p.phase,"project_type":p.project_type,
            "trades":list(ONTOLOGY.get(p.project_type,{})), "trade_basis":"project_type_expected",
            "source_url":r["source_url"],"quality_status":"VERIFIED_EARLY",
            "opportunity_score":None,"expected_tender_period":None,
            "location":project_locations.get(r["source_id"]),
            "authority_role":"planning_authority" if r.get("source_type")=="municipal_planning" else "buyer",
            "date_basis":"official_notice_date" if r.get("source_type")=="municipal_planning" else "publication",
            "project_history":history(evidence),
            "next_action":("Vorhabenträger und Bauabsicht in den Planunterlagen prüfen. Danach bei der Verfahrensstelle nach Ansprechpartner und Zeitplan fragen. Ein Planverfahren ist noch keine Bauzusage." if r.get("source_type")=="municipal_planning" else "Ansprechpartner in der Originalquelle ermitteln und nach dem geplanten Vergabezeitpunkt fragen.")})
    records=collapse_confirmed(records,historical.get("timelines",[]))
    out={"policy_version":POLICY_VERSION,"count":len(records),"opportunities":records,
        "notes":{"expected_trades":"Bei frühen Projekten aus der Projektart abgeleitet, noch keine bestätigten Lose.",
                 "dates":"Unbekannte Vergabezeiträume bleiben leer."}}
    (data/"bauradar_feed.json").write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding="utf-8")
    report={"early_signals":len(early),"master_projects":len(projects),
            "verified_early_projects":sum(r["quality_status"]=="VERIFIED_EARLY" for r in records),
            "customer_ted_records":sum(r["quality_status"]=="CONFIDENT" for r in records),
            "customer_ted_notices":len(tender["opportunities"]),"customer_records":len(records),"located_projects":sum(bool(r.get("location")) for r in records),
            "dresden_early_projects":sum(r.get("city")=="Dresden" and r["quality_status"]=="VERIFIED_EARLY" for r in records)}
    (ROOT/"reports"/"customer_feed_summary.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    print(json.dumps(report))
    return out

if __name__=="__main__": build()
