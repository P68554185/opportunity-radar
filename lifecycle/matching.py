"""Conservative, explainable project identity; scores are not probabilities.

Only independent identity evidence can confirm a link. Missing, contradictory,
ambiguous or undated evidence stays internal. Buyer office addresses must never
be supplied as construction addresses.
"""
from datetime import date
import re
import unicodedata

VERSION = "2026-10-06-identity-v1"
GENERIC = set("gymnasium stadtteilschule realschule mittelschule berufsschule pflegeschule zubau ersatzbau ersatzneubau generalsanierung gebaude zu neubau umbau sanierung erweiterung bau baumaßnahme projekt schule grundschule kindergarten klinikum krankenhaus hallenbad freibad gebäude campus stadt gemeinde landkreis los arbeiten rohbau trockenbau dach fassade vergabe ausschreibung der die das des den dem ein eine einer eines und oder am an im in mit für von zur zum".split())

def norm(value):
    value = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return " ".join(re.sub(r"[^\w]+", " ", value).split())

def published(value):
    # TED date-with-offset format has a date prefix, not a fabricated datetime.
    try:
        return date.fromisoformat(str(value)[:10])
    except (ValueError, TypeError):
        return None

def anchors(value):
    return {word for word in norm(value).split()
            if len(word) >= 4 and word not in GENERIC and not word.isdigit()}

def components(value):
    result={}
    for role,identifier in re.findall(r"(gebäude|bauteil|bauabschnitt|wache)\s+([a-z]|[ivx]+|\d+)\b",norm(value)):
        role="building" if role in ("gebäude","bauteil") else role
        result.setdefault(role,set()).add(identifier)
    return result

def childcare_roles(value):
    roles=set()
    text=norm(value)
    if re.search(r"\b(?:kinderhort(?:s)?|hort(?:s)?)\b",text): roles.add("hort")
    if re.search(r"\b(?:kinderkrippe|krippe)\b",text): roles.add("krippe")
    if re.search(r"\bkindergarten(?:s)?\b",text): roles.add("kindergarten")
    return roles

def childcare_conflict(a,b):
    ra,rb=childcare_roles(a),childcare_roles(b)
    return bool(ra and rb and ra.isdisjoint(rb))

def component_conflict(a,b):
    ca,cb=components(a),components(b)
    return any(ca[role].isdisjoint(cb[role]) for role in ca.keys() & cb.keys())

def evaluate(early, later, *, ambiguous=False):
    text_a = early.get("title", "")
    text_b = later.get("title", "")
    city_a, city_b = norm(early.get("city")), norm(later.get("city"))
    type_a, type_b = early.get("project_type"), later.get("project_type")
    address_a, address_b = norm(early.get("project_address")), norm(later.get("project_address"))
    shared = sorted(anchors(text_a) & anchors(text_b))
    evidence = {
        "same_city": bool(city_a and city_b and city_a == city_b),
        "same_type": bool(type_a and type_b and type_a == type_b),
        "same_project_address": bool(address_a and address_b and address_a == address_b),
        "same_project_reference": bool(early.get("project_reference") and
            early.get("project_reference") == later.get("project_reference")),
        "shared_name_anchors": shared,
        "same_authority": bool(norm(early.get("authority")) and
            norm(early.get("authority")) == norm(later.get("authority"))),
    }
    blockers = []
    if city_a and city_b and city_a != city_b:
        blockers.append("different_city")
    if type_a not in (None, "", "unknown") and type_b not in (None, "", "unknown") and type_a != type_b:
        blockers.append("different_project_type")
    if address_a and address_b and address_a != address_b:
        blockers.append("different_project_address")
    if childcare_conflict(text_a,text_b):
        blockers.append("different_childcare_facility")
    if component_conflict(text_a,text_b):
        blockers.append("different_building_component")
    start, end = published(early.get("published")), published(later.get("published"))
    if not start or not end:
        blockers.append("missing_publication_date")
    elif end <= start:
        blockers.append("non_forward_chronology")
    if later.get("phase") not in ("tender", "award", "prior_information"):
        blockers.append("not_procurement_event")
    if ambiguous:
        blockers.append("ambiguous_master_identity")
    # One common generic facility name, city/type or buyer alone is insufficient.
    strong_identity = (evidence["same_project_reference"] or
        evidence["same_project_address"] and bool(shared) or
        len(shared) >= 2 and evidence["same_authority"])
    supported = evidence["same_city"] and evidence["same_type"]
    status = "confirmed" if not blockers and strong_identity and supported else (
        "probable" if not blockers and supported and len(shared) >= 2 else
        "candidate" if not blockers and supported and shared else "unlinked")
    return {"version": VERSION, "status": status, "evidence": evidence,
        "blockers": blockers, "source_ids": [early.get("source_id"), later.get("source_id")],
        "publication_interval_days": (end-start).days if start and end and end > start else None,
        "interval_endpoint": later.get("phase"),
        "interpretation": "Source-publication interval to this notice; neither live detection lead nor first tender."}

def history(events):
    return sorted([{"source_id": e["source_id"], "source_url": e["source_url"],
        "published": e.get("published"), "phase": e.get("phase"), "title": e["title"]}
        for e in events], key=lambda e: (e.get("published") or "", e["source_id"]))
