import os,sys,json
ROOT=os.path.dirname(os.path.dirname(__file__));sys.path.insert(0,os.path.join(ROOT,"classification"))
from rules import classify
def first(d,*keys,default=""):
 for k in keys:
  v=d.get(k)
  if isinstance(v,list) and v:return v[0]
  if v not in (None,"",[]):return v
 return default
def normalize(n):
 nid=str(first(n,"publication-number","publicationNumber","id"))
 title=str(first(n,"notice-title","title",default=f"TED {nid}"))
 buyer=str(first(n,"buyer-name","buyerName")); place=first(n,"place-of-performance","placeOfPerformance",default="")
 cpv=first(n,"classification-cpv","cpv",default=[]); nt=str(first(n,"notice-type","noticeType",default="tender"))
 pt,tr=classify(title+" "+json.dumps({"place":place,"cpv":cpv},ensure_ascii=False))
 return {"source_id":"TED-"+nid,"source_type":"ted_live","source_url":f"https://ted.europa.eu/en/notice/-/detail/{nid}",
 "published":str(first(n,"publication-date","publicationDate")),"title":title,
 "body":json.dumps({"cpv":cpv,"place":place,"trades":tr},ensure_ascii=False),"authority":buyer,
 "city":"","region":"","country":"","project_type":pt,
 "phase":"award" if ("award" in nt.lower() or "result" in nt.lower()) else "tender","external_id":nid,"_trades":tr}
