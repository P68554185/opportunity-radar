"""Licensed municipal spatial references. Areas are not building entrances."""
import json, math, sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlencode
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from early.collect import Collector
from engine import haversine
BASE="https://kommisdd.dresden.de/net3/public/ogc.ashx"
ATTRIBUTION="Landeshauptstadt Dresden / Quelle: Geodaten Sachsen"
LICENSE="https://www.govdata.de/dl-de/by-2-0"
def parse_features(raw):
    root=ET.fromstring(raw)
    if root.tag.split("}")[-1]!="FeatureCollection":raise ValueError("Not a WFS feature collection")
    features=[]
    for member in root:
        if member.tag.split("}")[-1]!="member":continue
        feature=next(iter(member))
        props={e.tag.split("}")[-1]:(e.text or "").strip() for e in feature if len(e)==0}
        points=[]
        for element in feature.iter():
            if element.tag.split("}")[-1] in ("pos","posList"):
                values=list(map(float,(element.text or "").split()))
                if len(values)%2:raise ValueError("Unsupported coordinate dimensions")
                points.extend(zip(values[::2],values[1::2]))
        if not points:continue
        if not all(math.isfinite(lat) and math.isfinite(lon) and 50<lat<52 and 12<lon<15 for lat,lon in points):
            raise ValueError("Dresden CRS/axis mismatch")
        ys,xs=zip(*points)
        features.append({"id":feature.get("{http://www.opengis.net/gml/3.2}id"),"properties":props,"bbox":[min(xs),min(ys),max(xs),max(ys)]})
    return features,root.get("numberMatched","unknown")
def area_location(feature,source_url):
    west,south,east,north=feature["bbox"]
    lat=(south+north)/2;lon=(west+east)/2
    # A conservative covering circle, via the triangle inequality. Never a claimed precise site.
    extent=haversine(lat,lon,north,lon)+haversine(min(abs(south),abs(north)),lon,min(abs(south),abs(north)),east)
    return {"lat":lat,"lon":lon,"extent_km":math.ceil(extent*1000)/1000,
        "basis":"plan_area","source_url":source_url,"attribution":ATTRIBUTION,"license":LICENSE}
def fetch_features(client,node,typename,count):
    url=BASE+"?"+urlencode({"NodeId":node,"Service":"WFS","Request":"GetFeature","Version":"2.0.0","TypeNames":typename,"Count":count,"SrsName":"urn:ogc:def:crs:EPSG::4326"})
    raw,_=client.fetch(url)
    features,matched=parse_features(raw)
    if len(features)>=count:raise ValueError("Request limit reached; cannot claim a complete reference")
    if matched!="unknown" and int(matched)!=len(features):raise ValueError("Incomplete reference")
    return features,matched,url
def collect():
    client=Collector({"maximum_bytes":160_000_000,"timeout_seconds":90,"run_budget_seconds":240})
    report={"observed_at":datetime.now(timezone.utc).isoformat(),"attribution":ATTRIBUTION,"license":LICENSE,"sources":[]}
    snapshot_path=ROOT/"real_data/dresden_plan_reference.json"
    old=json.loads(snapshot_path.read_text()) if snapshot_path.exists() else {"plans":[]}
    all_plans={}
    for node,typename in [(489,"cls:L354"),(759,"cls:L575")]:
        try:
            # Require capability identity before using a new municipal layer.
            url=BASE+"?"+urlencode({"NodeId":node,"Service":"WFS","Request":"GetCapabilities"})
            raw,_=client.fetch(url)
            cap=ET.fromstring(raw)
            names={e.text for e in cap.iter() if e.tag.split("}")[-1]=="Name"}
            if typename not in names:raise ValueError("Unexpected municipal layer identity")
            features,matched,url=fetch_features(client,node,typename,1000)
            plans=[dict(f,source_url=url) for f in features if f["properties"].get("schluessel")]
            all_plans.update({f["id"]:f for f in plans})
            report["sources"].append({"node":node,"status":"verified","records":len(plans),"number_matched":matched})
        except Exception as exc:
            report["sources"].append({"node":node,"status":"refresh_failed_retained","detail":str(exc)[:160]})
    # Keep prior evidence from a layer that cannot currently be refreshed.
    kept={f["id"]:f for f in old["plans"]};kept.update(all_plans)
    snapshot_path.write_text(json.dumps({"plans":list(kept.values()),"attribution":ATTRIBUTION,"license":LICENSE},ensure_ascii=False,indent=2)+"\n")
    try:
        features,matched,url=fetch_features(client,184,"cls:L134",100000)
        addresses=[]
        for f in features:
            p=f["properties"]
            if p.get("status")!="A" or p.get("plz_ort")!="Dresden":continue
            west,south,east,north=f["bbox"]
            if west!=east or south!=north:raise ValueError("Address is not a point")
            addresses.append([str(p["adr_nr"]),p["adresse"]+" · "+p["plz_plz"]+" Dresden",south,west])
        if len(addresses)<1000:raise ValueError("Insufficient verified address coverage")
        data={"region":"Dresden","attribution":ATTRIBUTION,"license":LICENSE,"source_url":url,"observed_at":report["observed_at"],"addresses":addresses}
        (ROOT/"docs/data/pilot_locations.json").write_text(json.dumps(data,ensure_ascii=False,separators=(",",":"))+"\n")
        report["sources"].append({"node":184,"status":"verified","records":len(addresses),"number_matched":matched,
            "coverage":"Returned licensed municipal addresses; unknown numberMatched does not establish completeness"})
    except Exception as exc:
        report["sources"].append({"node":184,"status":"refresh_failed_retained","detail":str(exc)[:160]})
    (ROOT/"reports/dresden_geography.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(report,ensure_ascii=False))
    return report
def locations(events):
    path=ROOT/"real_data/dresden_plan_reference.json"
    if not path.exists():return {}
    plans=json.loads(path.read_text())["plans"];result={}
    for event in events:
        if event.get("source_type")!="municipal_planning" or event.get("city")!="Dresden":continue
        reference=event.get("project_reference","")
        key=reference.removeprefix("DRESDEN-PLAN-")
        matches=[p for p in plans if p["properties"].get("schluessel")==key]
        if len(matches)!=1:continue
        # Exact plan identity; visitor, buyer and contact addresses are never used.
        result[event["source_id"]]=area_location(matches[0],matches[0]["source_url"])
    return result
if __name__=="__main__":collect()
