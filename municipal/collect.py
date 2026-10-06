"""Refresh reviewed municipal notices; discovery never bypasses evidence review."""
import json, sys
from pathlib import Path
from datetime import datetime, timezone, date
from urllib.parse import urljoin
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from early.collect import Collector, validate_reviewed, safe_url
def collect():
    manifest=json.loads((ROOT/"real_data/dresden_source_manifest.json").read_text())
    output=ROOT/"real_data/municipal_verified_events.json"
    rows={r["source_id"]:r for r in json.loads(output.read_text())} if output.exists() else {}
    client=Collector(manifest["limits"])
    now=datetime.now(timezone.utc).isoformat()
    report={"region":"Dresden","observed_at":now,"sources":[],"review_queue":[]}
    registry_path=ROOT/"real_data/early_source_registry.json"
    registry={r["source_url"]:r for r in json.loads(registry_path.read_text())}
    for document in manifest["documents"]:
        url=document["source_url"]
        try:
            if not safe_url(url,"buergerbeteiligung.sachsen.de"):raise ValueError("Unapproved municipal host")
            if date.fromisoformat(document["published"])>date.today():raise ValueError("Future notice")
            page,digest=client.read(url)
            # The dated main notice alone qualifies; contact/sidebar addresses are not project locations.
            text=page.text.split("Kontakt")[0]
            events=validate_reviewed(document,text)
            for event in events:rows[event["source_id"]]=event
            result={"source_url":url,"status":"verified","records":len(events),"content_sha256":digest,"date_basis":"official_notice_date"}
            registry[url]=dict(result,status="official_verified",last_verified_at=now)
        except Exception as exc:
            result={"source_url":url,"status":"refresh_failed_retained","reason":type(exc).__name__,"detail":str(exc)[:180]}
        report["sources"].append(result)
    known={d["source_url"] for d in manifest["documents"]}
    for index in manifest["discovery"]:
        try:
            page,_=client.read(index["source_url"])
            urls=sorted({urljoin(index["source_url"],u).split("?")[0] for u in page.links})
            for url in urls:
                if safe_url(url,"buergerbeteiligung.sachsen.de") and "/portal/dresden/beteiligung/themen/" in url and url not in known:
                    report["review_queue"].append({"source_url":url,"reason":"Needs dated project goal and exact plan reference review"})
        except Exception as exc:
            report["sources"].append({"source_url":index["source_url"],"status":"discovery_failed","reason":type(exc).__name__})
    output.write_text(json.dumps(list(rows.values()),ensure_ascii=False,indent=2)+"\n")
    registry_path.write_text(json.dumps(list(registry.values()),ensure_ascii=False,indent=2)+"\n")
    (ROOT/"reports/municipal_collection.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))
    return report
if __name__=="__main__":collect()
