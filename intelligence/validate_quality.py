
from __future__ import annotations
import csv, json, random
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs" / "data"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
DOCS.mkdir(parents=True, exist_ok=True)

SAMPLE_SIZE = 60
SEED = 803

def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def extract_records():
    candidates = [
        DOCS / "opportunities.json",
        DOCS / "opportunity_feed.json",
        REPORTS / "intelligence.json",
        REPORTS / "opportunities.json",
        ROOT / "real_data" / "ted_live_normalized.json",
    ]
    for p in candidates:
        if not p.exists():
            continue
        obj = load_json(p)
        if isinstance(obj, list):
            return obj, str(p.relative_to(ROOT))
        if isinstance(obj, dict):
            for key in ("opportunities", "items", "records", "notices", "feed"):
                if isinstance(obj.get(key), list):
                    return obj[key], str(p.relative_to(ROOT))
    return [], None

def first(r, *keys, default=""):
    for k in keys:
        v = r.get(k)
        if v not in (None, "", [], {}):
            return v
    return default

def as_list(v):
    if isinstance(v, list): return v
    if v in (None, ""): return []
    return [v]

def confidence(r):
    raw = first(r, "confidence", "score", "opportunity_score", default=0)
    try:
        x = float(raw)
        if x > 1: x /= 100.0
        return max(0.0, min(1.0, x))
    except Exception:
        return 0.0

def evidence_strength(r):
    ptype = str(first(r, "project_type", "type", default="")).strip().lower()
    trades = as_list(first(r, "trades", "trade", "classified_trades", default=[]))
    cpv = str(first(r, "cpv", "cpv_code", "classification", default="")).strip()
    title = str(first(r, "title", "name", default="")).strip()
    desc = str(first(r, "description", "text", "summary", default="")).strip()
    points = 0
    reasons = []
    if ptype and ptype not in ("unknown","other","none"):
        points += 2; reasons.append("project_type")
    if trades:
        points += 2; reasons.append("trade")
    if cpv:
        points += 1; reasons.append("cpv")
    if len(title) >= 8:
        points += 1; reasons.append("title")
    if len(desc) >= 30:
        points += 1; reasons.append("description")
    return points, reasons

def quality_status(r):
    points, reasons = evidence_strength(r)
    conf = confidence(r)
    # Conservative output policy: weak evidence becomes UNKNOWN/review, never customer-facing HOT.
    if points >= 5 and conf >= 0.65:
        return "CONFIDENT", reasons
    if points >= 3:
        return "REVIEW", reasons
    return "UNKNOWN", reasons

records, source = extract_records()
enriched = []
for i, r in enumerate(records):
    if not isinstance(r, dict): 
        continue
    status, reasons = quality_status(r)
    item = dict(r)
    item["_quality"] = {
        "status": status,
        "confidence": round(confidence(r), 3),
        "evidence": reasons,
    }
    enriched.append(item)

counts = Counter(x["_quality"]["status"] for x in enriched)

# Stratified deterministic audit sample, favoring uncertain cases.
rng = random.Random(SEED)
buckets = {}
for status in ("CONFIDENT","REVIEW","UNKNOWN"):
    b = [x for x in enriched if x["_quality"]["status"] == status]
    rng.shuffle(b)
    buckets[status] = b
sample = []
targets = {"CONFIDENT":20, "REVIEW":25, "UNKNOWN":15}
for status, n in targets.items():
    sample.extend(buckets[status][:n])
if len(sample) < min(SAMPLE_SIZE, len(enriched)):
    used = {id(x) for x in sample}
    rest = [x for x in enriched if id(x) not in used]
    rng.shuffle(rest)
    sample.extend(rest[:SAMPLE_SIZE-len(sample)])

audit_rows = []
for idx, r in enumerate(sample, 1):
    audit_rows.append({
        "audit_id": idx,
        "notice_id": first(r, "notice_id", "id", "ted_id"),
        "title": first(r, "title", "name"),
        "description": first(r, "description", "text", "summary"),
        "cpv": first(r, "cpv", "cpv_code", "classification"),
        "project_type_predicted": first(r, "project_type", "type"),
        "trades_predicted": "; ".join(map(str, as_list(first(r, "trades", "trade", "classified_trades", default=[])))),
        "confidence": r["_quality"]["confidence"],
        "quality_status": r["_quality"]["status"],
        "evidence": "; ".join(r["_quality"]["evidence"]),
        # Human/AI review fields intentionally blank: no fabricated accuracy labels.
        "project_type_correct": "",
        "trades_correct": "",
        "false_positive": "",
        "review_notes": "",
    })

csv_path = REPORTS / "quality_audit_sample.csv"
with csv_path.open("w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=audit_rows[0].keys() if audit_rows else [
        "audit_id","notice_id","title","description","cpv","project_type_predicted",
        "trades_predicted","confidence","quality_status","evidence",
        "project_type_correct","trades_correct","false_positive","review_notes"
    ])
    w.writeheader()
    w.writerows(audit_rows)

summary = {
    "version": "0.8.3",
    "source": source,
    "records_seen": len(records),
    "records_evaluated": len(enriched),
    "quality_gate": dict(counts),
    "customer_facing_confident": counts.get("CONFIDENT",0),
    "held_for_review": counts.get("REVIEW",0),
    "suppressed_unknown": counts.get("UNKNOWN",0),
    "audit_sample_size": len(audit_rows),
    "accuracy_measured": False,
    "accuracy_note": "Precision/false-positive metrics require reviewed labels; no accuracy is fabricated.",
}
(REPORTS / "quality_validation_summary.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
(DOCS / "quality_validation.json").write_text(
    json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(summary, ensure_ascii=False, indent=2))
