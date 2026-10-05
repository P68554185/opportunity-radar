import os,sys,json,re
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,"classification"))
from rules import classify

LANG_ORDER=("deu","ger","eng")

def first(d,*keys,default=""):
 for k in keys:
  v=d.get(k)
  if v not in (None,"",[]):return v
 return default

def _preferred_text(v):
 if isinstance(v,str): return v
 if isinstance(v,list): return " ".join(_preferred_text(x) for x in v if x not in (None,""))
 if isinstance(v,dict):
  for lang in LANG_ORDER:
   if lang in v and v[lang] not in (None,"",[]): return _preferred_text(v[lang])
  vals=[_preferred_text(x) for x in v.values() if x not in (None,"",[])]
  return next((x for x in vals if x),"")
 return str(v or "")

def _all_text(v):
 if isinstance(v,str): return v
 if isinstance(v,list): return " ".join(_all_text(x) for x in v)
 if isinstance(v,dict): return " ".join(_all_text(x) for x in v.values())
 return str(v or "")

def _location(n,place):
 city=_preferred_text(first(n,"place-of-performance-city-proc",default=""))
 country=_preferred_text(first(n,"place-of-performance-country-proc",default=""))
 if not country:
  text=_all_text(place)
  country="DE" if re.search(r"\b(DEU|DE|Deutschland|Germany)\b",text,re.I) else ""
 return city,"",country

def normalize(n):
 nid=str(first(n,"publication-number","publicationNumber","id"))
 title=_preferred_text(first(n,"title-proc","notice-title","title",default=f"TED {nid}"))
 buyer=_preferred_text(first(n,"buyer-name","buyerName"))
 place=first(n,"place-of-performance","placeOfPerformance",default="")
 cpv=first(n,"classification-cpv","cpv",default=[])
 nt=_preferred_text(first(n,"notice-type","noticeType",default="tender"))
 # Classification uses one preferred-language title plus structured CPV, not all 24 TED translations.
 body_text=" ".join([title,buyer,_preferred_text(place)])
 pt,tr=classify(body_text,cpv)
 city,region,country=_location(n,place)
 return {"source_id":"TED-"+nid,"source_type":"ted_live","source_url":f"https://ted.europa.eu/en/notice/-/detail/{nid}",
 "published":str(first(n,"publication-date","publicationDate")),"title":title,
 "body":json.dumps({"cpv":cpv,"place":place,"trades":tr},ensure_ascii=False),"authority":buyer,
 "city":city,"region":region,"country":country,"project_type":pt,
 "phase":"award" if ("award" in nt.lower() or "result" in nt.lower() or "can-" in nt.lower()) else "tender",
 "external_id":nid,"_trades":tr}
