"""
Opportunity Engine v0.3
Source -> Event -> Entity resolution -> Master Project -> Trade opportunities -> Company matches

Pure-Python reference implementation. External collectors are adapters; this core can be
connected to TED, German/Bavarian open data, municipal feeds, or stored JSON records.
"""
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import date
from difflib import SequenceMatcher
from math import radians, sin, cos, sqrt, atan2
from typing import Optional
import hashlib, json, re

PHASE_SCORE = {
    "project_announced": 25, "prior_information": 92, "idea": 25, "political_decision": 38, "funding": 50,
    "object_planning": 66, "specialist_planning": 82,
    "execution_planning": 90, "tender": 98, "award": 100,
}
TIMING_SCORE = {
    "idea": 25, "political_decision": 35, "funding": 45,
    "object_planning": 65, "specialist_planning": 82,
    "execution_planning": 92, "tender": 100, "award": 20,
}

# v0.2 ontology: deliberately broad. We refine probabilities from observed historical data later.
ONTOLOGY = {
    "school": {
        "earthworks": .95, "structural": .99, "scaffolding": .90, "roof": .95,
        "facade": .94, "windows_doors": .98, "electrical": .99, "hvac": .99,
        "building_automation": .82, "fire_protection": .96, "drywall": .96,
        "screed": .94, "flooring": .96, "painting": .96, "metalwork": .88,
        "landscaping": .96,
    },
    "kindergarten": {
        "earthworks": .95, "structural": .99, "roof": .97, "facade": .92,
        "windows_doors": .98, "electrical": .99, "hvac": .99, "fire_protection": .93,
        "drywall": .95, "flooring": .96, "painting": .96, "landscaping": .98,
    },
    "fire_station": {
        "earthworks": .98, "structural": .99, "steelwork": .90, "roof": .98,
        "facade": .90, "windows_doors": .96, "industrial_doors": .99,
        "electrical": .99, "hvac": .99, "building_automation": .80,
        "fire_protection": .92, "drywall": .90, "flooring": .92,
        "painting": .92, "metalwork": .92, "landscaping": .98,
    },
    "hospital": {
        "earthworks": .90, "structural": .99, "roof": .96, "facade": .97,
        "windows_doors": .98, "electrical": .99, "hvac": .99,
        "building_automation": .98, "fire_protection": .99, "drywall": .98,
        "flooring": .98, "painting": .97, "medical_technology": .95,
        "elevators": .94, "landscaping": .90,
    },
}

@dataclass
class SourceEvent:
    source_id: str
    source_type: str
    source_url: str
    published: str
    title: str
    body: str
    authority: str = ""
    city: str = ""
    region: str = ""
    country: str = "DE"
    lat: Optional[float] = None
    lon: Optional[float] = None
    project_type: str = ""
    phase: str = ""
    value_eur: Optional[float] = None
    funding_eur: Optional[float] = None
    external_id: str = ""
    project_address: str = ""
    project_reference: str = ""

@dataclass
class Project:
    project_id: str
    canonical_name: str
    city: str
    region: str
    country: str
    project_type: str
    phase: str
    project_confidence: float
    lat: Optional[float] = None
    lon: Optional[float] = None
    value_eur: Optional[float] = None
    funding_eur: Optional[float] = None
    event_ids: list[str] = field(default_factory=list)
    authority: str = ""
    project_address: str = ""
    project_reference: str = ""
    latest_published: str = ""
    history: list[dict] = field(default_factory=list)

@dataclass
class Company:
    company_id: str
    name: str
    trades: list[str]
    lat: float
    lon: float
    radius_km: float
    min_project_eur: float = 0
    max_project_eur: float = 1e12

def norm(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9äöüß ]+", " ", s)
    return " ".join(s.split())

def event_key(e: SourceEvent) -> str:
    raw = "|".join([e.source_type, e.external_id or e.source_url, e.title, e.published])
    return hashlib.sha256(raw.encode()).hexdigest()[:20]

def project_similarity(a: Project, e: SourceEvent) -> float:
    from lifecycle.matching import anchors, component_conflict, childcare_conflict
    if a.project_address and e.project_address and norm(a.project_address)!=norm(e.project_address):
        return 0.0
    if a.project_reference and e.project_reference and a.project_reference!=e.project_reference:
        return 0.0
    if component_conflict(a.canonical_name,e.title) or childcare_conflict(a.canonical_name,e.title): return 0.0
    # Shared generic facility words alone do not identify one construction project.
    shared=(anchors(a.canonical_name)&anchors(e.title))-set(norm(a.city).split())
    if not shared and not (a.project_address and a.project_address==e.project_address) and not (
            a.project_reference and a.project_reference==e.project_reference):
        return 0.0
    # v0.4 safety gate: two known, different municipalities cannot auto-merge.
    if a.project_type not in ("", "unknown") and e.project_type and a.project_type != e.project_type:
        return 0.0
    if a.city and e.city and norm(a.city) != norm(e.city):
        return 0.0
    city = 1.0 if norm(a.city) == norm(e.city) and a.city else 0.0
    typ = 1.0 if a.project_type and a.project_type == e.project_type else 0.0
    title = SequenceMatcher(None, norm(a.canonical_name), norm(e.title)).ratio()
    return .45*city + .25*typ + .30*title

def resolve_project(projects: list[Project], e: SourceEvent, threshold=.78) -> Project:
    key=event_key(e)
    for existing in projects:
        if key in existing.event_ids:
            return existing
    candidates = [(project_similarity(p,e),p) for p in projects]
    if candidates:
        candidates.sort(key=lambda x:x[0], reverse=True)
        score, best = candidates[0]
        gap = score-candidates[1][0] if len(candidates)>1 else 1.0
        title_similarity = SequenceMatcher(None, norm(best.canonical_name), norm(e.title)).ratio()
        if event_key(e) in best.event_ids:
            return best
        if score >= threshold and gap >= .07 and title_similarity >= .50:
            best.event_ids.append(event_key(e))
            if e.published and e.published>=best.latest_published:
                best.phase = e.phase or best.phase
                best.latest_published = e.published
            best.authority = best.authority or e.authority
            best.project_address = best.project_address or e.project_address
            best.project_reference = best.project_reference or e.project_reference
            best.history.append({"source_id":e.source_id,"source_url":e.source_url,
                "published":e.published,"phase":e.phase,"title":e.title})
            best.history.sort(key=lambda r:(r["published"],r["source_id"]))
            best.project_confidence = max(best.project_confidence, PHASE_SCORE.get(e.phase,35))
            best.value_eur = e.value_eur or best.value_eur
            best.funding_eur = e.funding_eur or best.funding_eur
            return best
    pid = "PRJ-" + hashlib.sha1(f"{norm(e.city)}|{norm(e.title)}|{e.project_type}|{e.country}".encode()).hexdigest()[:10].upper()
    if any(p.project_id==pid for p in projects):
        pid=pid+"-"+event_key(e)[:6].upper()
    p = Project(pid, e.title, e.city, e.region, e.country, e.project_type or "unknown",
                e.phase or "idea", PHASE_SCORE.get(e.phase,35), e.lat,e.lon,
                e.value_eur,e.funding_eur,[event_key(e)])
    p.authority=e.authority
    p.project_address=e.project_address
    p.project_reference=e.project_reference
    p.latest_published=e.published
    p.history=[{"source_id":e.source_id,"source_url":e.source_url,
        "published":e.published,"phase":e.phase,"title":e.title}]
    projects.append(p)
    return p

def trade_opportunities(p: Project):
    trades = ONTOLOGY.get(p.project_type,{})
    for trade, prob in trades.items():
        trade_conf = round(prob*100)
        # specialist planning raises confidence for TGA-like trades
        if p.phase in ("specialist_planning","execution_planning","tender") and trade in {
            "electrical","hvac","building_automation","fire_protection"}:
            trade_conf = min(100, trade_conf + 2)
        yield {
            "project_id":p.project_id, "trade":trade,
            "project_confidence":p.project_confidence,
            "trade_confidence":trade_conf,
            "timing_score":TIMING_SCORE.get(p.phase,30),
        }

def haversine(lat1,lon1,lat2,lon2):
    R=6371.0
    dlat=radians(lat2-lat1); dlon=radians(lon2-lon1)
    a=sin(dlat/2)**2+cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return 2*R*atan2(sqrt(a),sqrt(1-a))

def match(company: Company, p: Project, opp: dict):
    if opp["trade"] not in company.trades or p.lat is None or p.lon is None:
        return None
    d=haversine(company.lat,company.lon,p.lat,p.lon)
    if d>company.radius_km: return None
    distance_score=max(0,100*(1-d/company.radius_km))
    size_score=75
    if p.value_eur:
        size_score = 100 if company.min_project_eur <= p.value_eur <= company.max_project_eur else 45
    score=(.30*opp["project_confidence"]+.25*opp["trade_confidence"]+
           .15*opp["timing_score"]+.10*distance_score+.10*size_score+.10*80)
    score=round(score,1)
    band="HOT" if score>=85 else "UPCOMING" if score>=65 else "EARLY" if score>=45 else "HIDDEN"
    return {"company_id":company.company_id,"project_id":p.project_id,"trade":opp["trade"],
            "distance_km":round(d,1),"score":score,"band":band}

def ingest(events):
    projects=[]
    seen=set()
    for raw in events:
        e=SourceEvent(**raw)
        k=event_key(e)
        if k in seen: continue
        seen.add(k)
        resolve_project(projects,e)
    return projects
