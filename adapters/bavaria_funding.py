"""Bavarian funding/program text parser.

Parses concrete list-like measures such as:
'Stadt X: 1,5 Millionen Euro für den Neubau einer Grundschule mit Sporthalle'
into early SourceEvents. Conservative: ambiguous lines go to quarantine.
"""
from __future__ import annotations
import re, hashlib

TYPE_RULES=[
 ("school",r"\b(grundschule|mittelschule|realschule|gymnasium|schule|schulzentrum|berufsschule)\b"),
 ("kindergarten",r"\b(kita|kindertageseinrichtung|kindergarten|kinderhaus|hort)\b"),
 ("fire_station",r"\b(feuerwehrhaus(?:es)?|feuerwache|feuerwehrgerätehaus(?:es)?)\b"),
 ("hospital",r"\b(klinikum(?:s)?|krankenhaus(?:es)?|klinik)\b"),
]
ACTION=r"(neubau|ersatzneubau|erweiterung|generalsanierung|sanierung|umbau)"

def classify(text):
    t=text.lower()
    for typ,pat in TYPE_RULES:
        if re.search(pat,t): return typ
    return ""

def parse_eur(s):
    s=s.replace(".","").replace(",",".")
    return float(s)

def parse_measure(line, source_url, published, region="Bayern"):
    # Accepts € / Euro and million wording.
    m=re.search(r"^\s*[•\-]?\s*(?P<authority>[^:]{2,100}):\s*"
                r"(?P<amount>\d+(?:[.,]\d+)?)\s*(?P<unit>Million(?:en)?|Mio\.?)?\s*Euro"
                r"\s+für\s+(?P<title>.+?)\s*$",line,re.I)
    if not m: return None, "pattern_miss"
    amount=parse_eur(m.group("amount"))
    if m.group("unit"): amount*=1_000_000
    title=m.group("title").strip(" .")
    typ=classify(title)
    if not typ: return None, "unsupported_project_type"
    authority=m.group("authority").strip()
    city=re.sub(r"^(Stadt|Gemeinde|Markt|Landkreis|Schulverband)\s+","",authority,flags=re.I).strip()
    sid=hashlib.sha1((source_url+"|"+authority+"|"+title).encode()).hexdigest()[:16]
    return {
      "source_id":"BYF-"+sid,"source_type":"bavaria_funding",
      "source_url":source_url,"published":published,
      "title":title,"body":line.strip(),"authority":authority,
      "city":city,"region":region,"country":"DE","project_type":typ,
      "phase":"funding","funding_eur":amount,"external_id":sid
    }, None

def parse_document(text, source_url, published):
    events=[]; quarantine=[]
    for line in text.splitlines():
        if " Euro " not in f" {line} " and "Euro" not in line: continue
        ev,err=parse_measure(line,source_url,published)
        if ev: events.append(ev)
        elif ":" in line: quarantine.append({"line":line.strip(),"reason":err})
    return events,quarantine
