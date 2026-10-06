"""Bounded public-source refresh and discovery. No credentials or paid APIs.

Existing verified evidence is retained on collection failures. Unknown layouts,
dates, county locations and unsupported sources go to review, never the feed.
"""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import time
from urllib.parse import urljoin, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.error import HTTPError
from urllib.robotparser import RobotFileParser
from datetime import datetime, timezone, date

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from adapters.bavaria_funding import parse_document, ACTION
from lifecycle.matching import norm

USER_AGENT="BauRadar/1.0 (+https://p68554185.github.io/opportunity-radar/)"
class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]; self.links=[]; self.skip=0; self.publication_dates=[]; self.link_titles={}; self.current_link=None; self.link_text=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="meta" and attrs.get("property")=="article:published_time":
            self.publication_dates.append(attrs.get("content",""))
        if tag in ("script","style"): self.skip+=1
        if tag in ("p","li","br","h1","h2","h3"): self.parts.append("\n")
        if tag=="a":
            href=dict(attrs).get("href")
            if href:
                self.links.append(href); self.current_link=href; self.link_text=[]
    def handle_endtag(self,tag):
        if tag=="a" and self.current_link:
            self.link_titles[self.current_link]=" ".join(self.link_text)
            self.current_link=None; self.link_text=[]
        if tag in ("script","style") and self.skip: self.skip-=1
        if tag in ("p","li","h1","h2","h3"): self.parts.append("\n")
    def handle_data(self,data):
        if self.current_link: self.link_text.append(data)
        if not self.skip: self.parts.append(data)
    @property
    def text(self):
        return "\n".join(" ".join(line.split()) for line in "".join(self.parts).splitlines() if line.strip())

class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        if urlparse(newurl).scheme!="https" or urlparse(newurl).hostname!=urlparse(req.full_url).hostname:
            raise ValueError("Cross-host redirect blocked")
        return super().redirect_request(req,fp,code,msg,headers,newurl)

def safe_url(url,host):
    p=urlparse(url)
    return p.scheme=="https" and p.hostname==host and not p.username and not p.password and p.port in (None,443)

class Collector:
    def __init__(self,limits):
        self.limits=limits; self.robots={}; self.last={}; self.opener=build_opener(SameHostRedirect()); self.started=time.monotonic()
    def raw(self,url):
        request=Request(url,headers={"User-Agent":USER_AGENT})
        with self.opener.open(request,timeout=self.limits["timeout_seconds"]) as response:
            raw=response.read(self.limits["maximum_bytes"]+1)
            if len(raw)>self.limits["maximum_bytes"]: raise ValueError("Source size limit")
            return raw.decode(response.headers.get_content_charset() or "utf-8",errors="replace")
    def read(self,url):
        if time.monotonic()-self.started>120: raise TimeoutError("EARLY collection run budget exhausted")
        host=urlparse(url).hostname
        if not safe_url(url,host): raise ValueError("Unsafe source URL")
        if host not in self.robots:
            robots_url="https://"+host+"/robots.txt"
            rp=RobotFileParser(); rp.set_url(robots_url)
            try:
                rp.parse(self.raw(robots_url).splitlines())
            except HTTPError as exc:
                if exc.code not in (404,410): raise
                rp.parse([])
            self.robots[host]=rp
        if not self.robots[host].can_fetch(USER_AGENT,url): raise ValueError("Robots disallows source")
        delay=max(1,float(self.robots[host].crawl_delay(USER_AGENT) or 0))
        if delay>10: raise ValueError("Source crawl delay requires a dedicated schedule")
        time.sleep(max(0,delay-(time.monotonic()-self.last.get(host,0))))
        raw=self.raw(url); self.last[host]=time.monotonic()
        parsed=Text(); parsed.feed(raw)
        return parsed,hashlib.sha256(raw.encode()).hexdigest()

def validate_reviewed(document,text):
    if document["date_anchor"] not in text:
        raise ValueError("Expected publication date absent")
    accepted=[]
    for row in document["records"]:
        if norm(row["required_anchor"]) not in norm(text):
            raise ValueError("Reviewed project absent from current source")
        event=row["event"]
        if event["published"]!=document["published"] or event["source_url"]!=document["source_url"]:
            raise ValueError("Manifest identity mismatch")
        accepted.append(event)
    return accepted

def collect():
    manifest=json.loads((ROOT/"real_data/early_source_manifest.json").read_text())
    output=ROOT/"real_data/early_verified_events.json"
    existing=json.loads(output.read_text()) if output.exists() else []
    indexed={r["source_id"]:r for r in existing}
    report={"observed_at":datetime.now(timezone.utc).isoformat(),"sources":[],"review_queue":[]}
    client=Collector(manifest["limits"])
    for document in manifest["documents"]:
        url=document["source_url"]
        try:
            page,digest=client.read(url)
            events=validate_reviewed(document,page.text+" "+" ".join(page.publication_dates))
            for event in events: indexed[event["source_id"]]=event
            report["sources"].append({"source_url":url,"status":"verified","content_sha256":digest,"records":len(events)})
        except Exception as exc:
            report["sources"].append({"source_url":url,"status":"refresh_failed_retained","reason":type(exc).__name__})
    seen={d["source_url"] for d in manifest["documents"]}
    seen.update(r["source_url"] for r in json.loads((ROOT/"real_data/bavaria_verified_events.json").read_text()))
    budget=manifest["limits"]["maximum_documents"]
    for discovery in manifest["discovery"]:
        try:
            page,_=client.read(discovery["source_url"])
            links=sorted({urljoin(discovery["source_url"],link) for link in page.links
                if re.search(r"hochbau|krankenhaus|kinder|schul|förderbescheid|neubau|bauvorhaben",page.link_titles.get(link,""),re.I)},reverse=True)
            for url in links:
                if url in seen or not safe_url(url,discovery["host"]): continue
                if not re.search(r"/pressemitteilungen/(?:\d+/|[^/]+-\d+$)",url): continue
                if budget<=0: break
                budget-=1; seen.add(url)
                if discovery["adapter"]=="review_queue":
                    report["review_queue"].append({"source_url":url,"reason":"needs_dated_source_adapter"})
                    continue
                candidate,digest=client.read(url)
                date_match=re.search(r"München,\s*(\d{2})\.(\d{2})\.(\d{4})",candidate.text)
                if not date_match:
                    report["review_queue"].append({"source_url":url,"reason":"unproven_publication_date"}); continue
                day,month,year=map(int,date_match.groups()); issued=date(year,month,day)
                if not 0<=(date.today()-issued).days<=365: continue
                events,quarantine=parse_document(candidate.text,url,issued.isoformat())
                accepted=[]
                for event in events:
                    if not re.search(ACTION,event["title"],re.I) or event["authority"].startswith(("Landkreis","Schulverband")):
                        report["review_queue"].append({"source_url":url,"reason":"construction_or_municipality_not_proven"}); continue
                    event["body"]="Öffentliche Fördermeldung zu einer konkret benannten Baumaßnahme."
                    indexed[event["source_id"]]=event; accepted.append(event)
                if accepted:
                    report["sources"].append({"source_url":url,"status":"verified","content_sha256":digest,"records":len(accepted)})
        except Exception as exc:
            report["sources"].append({"source_url":discovery["source_url"],"status":"discovery_failed","reason":type(exc).__name__})
    registry_path=ROOT/"real_data/early_source_registry.json"
    registry=json.loads(registry_path.read_text()) if registry_path.exists() else []
    official={r["source_url"]:r for r in registry}
    for result in report["sources"]:
        if result["status"]=="verified":
            official[result["source_url"]]=dict(result,status="official_verified",last_verified_at=report["observed_at"])
    registry_path.write_text(json.dumps(list(official.values()),ensure_ascii=False,indent=2)+"\n")
    output.write_text(json.dumps(list(indexed.values()),ensure_ascii=False,indent=2)+"\n")
    (ROOT/"reports/early_collection.json").write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({"source_checks":report["sources"],"discovered_review_candidates":report["review_queue"]},ensure_ascii=False))
    print(json.dumps({"verified_sources":sum(r["status"]=="verified" for r in report["sources"]),
        "retained_signals":len(indexed),"review_candidates":len(report["review_queue"])}))
    return report
if __name__=="__main__": collect()
