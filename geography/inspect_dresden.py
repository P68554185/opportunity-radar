"""Inspect public Dresden WFS schemas before selecting bounded geodata queries."""
import json
import xml.etree.ElementTree as ET
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE="https://kommisdd.dresden.de/net3/public/ogc.ashx"
results={}
for kind,node in [("plans",489),("development_plans",759),("addresses",184)]:
    url=BASE+"?"+urlencode({"NodeId":node,"Service":"WFS","Request":"GetCapabilities"})
    try:
        with urlopen(Request(url,headers={"User-Agent":"BauRadar/1.0"}),timeout=30) as r:raw=r.read(4_000_001)
        root=ET.fromstring(raw)
        types=[{"name":next((e.text for e in t if e.tag.split("}")[-1]=="Name"),""),
                "title":next((e.text for e in t if e.tag.split("}")[-1]=="Title"),"")}
                for t in root.iter() if t.tag.split("}")[-1]=="FeatureType"]
        params=[{"tag":e.tag.split("}")[-1],"text":(e.text or "").strip()} for e in root.iter() if e.tag.split("}")[-1] in ("DefaultSRS","OtherSRS","DefaultCRS","OtherCRS","Value")]
        result={"types":types,"parameters":params,"version":root.get("version")}
        results[kind]=result;print(json.dumps({kind:result},ensure_ascii=False))
        name=types[0]["name"]
        query={"NodeId":node,"Service":"WFS","Request":"GetFeature","Version":"2.0.0","TypeNames":name,"Count":100000 if kind=="addresses" else 1000,"SrsName":"urn:ogc:def:crs:EPSG::4326"}
        with urlopen(Request(BASE+"?"+urlencode(query),headers={"User-Agent":"BauRadar/1.0"}),timeout=90) as response:raw=response.read(160_000_001)
        doc=ET.fromstring(raw)
        features=[]
        for member in doc:
            if member.tag.split("}")[-1]!="member":continue
            feature=next(iter(member))
            properties={e.tag.split("}")[-1]:(e.text or "").strip() for e in feature if len(e)==0}
            points=[]
            for e in feature.iter():
                tag=e.tag.split("}")[-1]
                if tag in ("posList","pos"):
                    values=list(map(float,(e.text or "").split()))
                    if len(values)%2:raise ValueError("Unexpected coordinate dimensions")
                    points.extend([values[i:i+2] for i in range(0,len(values),2)])
            if not points:continue
            # WFS 2 / EPSG:4326 GML uses latitude, longitude axis order.
            ys=[p[0] for p in points];xs=[p[1] for p in points]
            if not all(50<lat<52 and 12<lon<15 for lat,lon in points):raise ValueError("Unexpected CRS/axis")
            features.append({"id":feature.get("{http://www.opengis.net/gml/3.2}id"),"properties":properties,"bbox":[min(xs),min(ys),max(xs),max(ys)]})
        if kind=="addresses":
            features=[f for f in features if f["properties"].get("status")=="A"]
            for f in features:f["properties"]={k:v for k,v in f["properties"].items() if k in ("adresse","plz_plz","plz_ort","adr_nr")}
        result["features"]=features;result["numberMatched"]=doc.get("numberMatched")
        print(json.dumps({"kind":kind,"count":len(features),"matched":doc.get("numberMatched"),"sample":features[:4],"candidates":[f for f in features if any(s in str(f["properties"]) for s in ["3065","3082","6066","3068","3028","3027 B","6058"])]},ensure_ascii=False))
    except Exception as exc:print(json.dumps({"kind":kind,"error":str(exc)}))
(ROOT/"reports/dresden_source_schema.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
