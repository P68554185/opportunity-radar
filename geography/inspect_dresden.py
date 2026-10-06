"""Inspect public Dresden WFS schemas before selecting bounded geodata queries."""
import json
import xml.etree.ElementTree as ET
from urllib.request import urlopen,Request
from urllib.parse import urlencode
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE="https://kommisdd.dresden.de/net3/public/ogc.ashx"
results={}
for kind,node in [("plans",489),("addresses",184)]:
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
    except Exception as exc:print(json.dumps({"kind":kind,"error":str(exc)}))
(ROOT/"reports/dresden_source_schema.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n")
