import os,sys,json,re
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,"classification"))
from rules import classify

def first(d,*keys,default=""):
 for k in keys:
  v=d.get(k)
  if isinstance(v,list) and v:return v[0]
  if v not in (None,"",[]):return v
 return default

def _flatten_text(v):
 if isinstance(v,str): return v
 if isinstance(v,list): return " ".join(_flatten_text(x) for x in v)
 if isinstance(v,dict): return " ".join(_flatten_text(x) for x in v.values())
 return str(v or "")

def _location(place):
 text=_flatten_text(place)
 country="DE" if re.search(r"\b(DE|Deutschland|Germany)\b",text,re.I) else ""
 # Defensive extraction only; never invent a municipality.
 city=""
 if isinstance(place,dict):
  city=str(place.get("city") or place.get("locality") or place.get("town") or "")
 elif isinstance(place,list):
  for x in place:
   if isinstance(x,dict) and not city: city=str(x.get("city") or x.get("locality") or x.get("town") or "")
 return city,"",country

def normalize(n):
 nid=str(first(n,"publication-number","publicationNumber","id"))
 title=_flatten_text(first(n,"notice-title","title",default=f"TED {nid}"))
 buyer=_flatten_text(first(n,"buyer-name","buyerName")); place=first(n,"place-of-performance","placeOfPerformance",default="")
 cpv=first(n,"classification-cpv","cpv",default=[]); nt=str(first(n,"notice-type","noticeType",default="tender"))
 body_text=" ".join([title,buyer,_flatten_text(place),_flatten_text(cpv)])
 pt,tr=classify(body_text,cpv)
 city,region,country=_location(place)
 return {"source_id":"TED-"+nid,"source_type":"ted_live","source_url":f"https://ted.europa.eu/en/notice/-/detail/{nid}",
 "published":str(first(n,"publication-date","publicationDate")),"title":title,
 "body":json.dumps({"cpv":cpv,"place":place,"trades":tr},ensure_ascii=False),"authority":buyer,
 "city":city,"region":region,"country":country,"project_type":pt,
 "phase":"award" if ("award" in nt.lower() or "result" in nt.lower()) else "tender","external_id":nid,"_trades":tr}
