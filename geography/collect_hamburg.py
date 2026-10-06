"""Acquire licensed public Hamburg reference facts; never customer/account data."""
import json,time,hashlib
from pathlib import Path
from datetime import datetime,timezone
from urllib.request import Request,build_opener,HTTPRedirectHandler
from urllib.parse import urlparse,urlencode
ROOT=Path(__file__).resolve().parents[1]
BASE="https://api.hamburg.de/datasets/v1/"
DATASETS={"plans":"bplaene/collections/prosin_imverfahren","districts":"verwaltungsgrenzen/collections/stadtteile","schools":"schulen/collections/staatliche_schulen"}
class RestrictedRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urlparse(newurl).scheme!="https" or urlparse(newurl).hostname!="api.hamburg.de":raise ValueError("Unexpected redirect")
        return super().redirect_request(req,fp,code,msg,headers,newurl)
def coordinates(value):
    if isinstance(value,list):
        if len(value)>=2 and all(isinstance(x,(float,int)) and not isinstance(x,bool) for x in value[:2]):
            yield value[:2]
        else:
            for part in value:yield from coordinates(part)
def summarize(feature):
    geometry=feature.get("geometry") or {}
    points=list(coordinates(geometry.get("coordinates",[])))
    if not points:raise ValueError("No geometry")
    if any(not (7<lon<11 and 53<lat<55) for lon,lat in points):raise ValueError("Unexpected CRS/location")
    xs=[p[0] for p in points];ys=[p[1] for p in points]
    return {"id":feature["id"],"properties":feature.get("properties",{}),
            "geometry_type":geometry.get("type"),"bbox":[min(xs),min(ys),max(xs),max(ys)]}
def collect():
    opener=build_opener(RestrictedRedirect())
    report={"observed_at":datetime.now(timezone.utc).isoformat(),"sources":[]}
    target=ROOT/"real_data/hamburg_open_data_snapshot.json"
    state=json.loads(target.read_text()) if target.exists() else {}
    for kind,path in DATASETS.items():
        url=BASE+path+"/items?"+urlencode({"f":"json","limit":250})
        features=[];seen=set()
        try:
            for page in range(4):
                if url in seen:raise ValueError("Repeated pagination")
                seen.add(url)
                with opener.open(Request(url,headers={"Accept":"application/geo+json","User-Agent":"BauRadar/1.0 (+https://p68554185.github.io/opportunity-radar/)"}),timeout=30) as response:
                    raw=response.read(16_000_001)
                if len(raw)>16_000_000:raise ValueError("Size limit")
                payload=json.loads(raw)
                if payload.get("type")!="FeatureCollection":raise ValueError("Expected GeoJSON")
                features.extend(summarize(f) for f in payload["features"])
                links=[l["href"] for l in payload.get("links",[]) if l.get("rel")=="next"]
                if not links:break
                url=links[0]
                p=urlparse(url)
                if p.scheme!="https" or p.hostname!="api.hamburg.de" or not p.path.startswith("/datasets/v1/"+path+"/items"):raise ValueError("Unsafe pagination")
                time.sleep(1)
            else:raise ValueError("Pagination budget exhausted")
            if not features or len({str(f["id"]) for f in features})!=len(features):raise ValueError("Incomplete or duplicate features")
            state[kind]={"source_url":BASE+path,"license":"dl-de/by-2-0","license_url":"https://www.govdata.de/dl-de/by-2-0","attribution":"Freie und Hansestadt Hamburg; "+("Behörde für Stadtentwicklung und Wohnen" if kind=="plans" else "Landesbetrieb Geoinformation und Vermessung" if kind=="districts" else "Behörde für Schule, Familie und Berufsbildung"),
                         "observed_at":report["observed_at"],"features":features}
            report["sources"].append({"kind":kind,"status":"verified","records":len(features)})
            print(json.dumps({"kind":kind,"records":len(features),"sample":features[:2]},ensure_ascii=False))
        except Exception as exc:
            report["sources"].append({"kind":kind,"status":"refresh_failed_retained","reason":type(exc).__name__,"detail":str(exc)[:200]})
            print(json.dumps(report["sources"][-1]))
    target.write_text(json.dumps(state,ensure_ascii=False,indent=2)+"\n")
    (ROOT/"reports/hamburg_geodata_collection.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return report
if __name__=="__main__":collect()
