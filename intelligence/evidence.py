"""Deterministic evidence screening. Scores are rule strengths, not accuracy."""
import math
from urllib.parse import urlparse
from classification.rules import classify, _cpvs

POLICY_VERSION = "2026-10-05-evidence-v1"

def evidence_for(title, cpv):
    codes = [c for c in _cpvs(cpv) if len(c) in (8, 9) and c.startswith("45")]
    text_project, text_trades = classify(title, [])
    cpv_project, cpv_trades = classify("", codes)
    project = text_project or cpv_project
    trades = list(dict.fromkeys(text_trades + cpv_trades))
    # CPV-only project labels and generic construction titles require human review.
    strength = .85 if text_project and set(text_trades) & set(cpv_trades) else (
        .75 if text_project and trades and codes else .55 if project and trades else .35 if project or trades else 0)
    return project, trades, strength, {
        "project_text": bool(text_project), "project_cpv": bool(cpv_project),
        "trade_text": text_trades, "trade_cpv": cpv_trades,
        "construction_cpv": codes, "policy_version": POLICY_VERSION,
        "confidence_note": "Rule-based evidence strength; not measured accuracy."
    }

def classify_evidence(record):
    # Never fall back to commercial score or the legacy confidence field.
    try:
        confidence = float(record.get("classification_confidence", 0))
        if not math.isfinite(confidence): confidence = 0
    except (TypeError, ValueError):
        confidence = 0
    confidence = max(0, min(1, confidence))
    project = record.get("project_type") not in (None, "", "unknown", "other", "none")
    trades = bool([t for t in record.get("trades", []) if isinstance(t, str) and t.strip()])
    cpv = bool([c for c in _cpvs(record.get("cpv")) if len(c) in (8, 9) and c.startswith("45")])
    text = len(str(record.get("title") or "").strip()) >= 10
    url = urlparse(str(record.get("source_url") or ""))
    source = url.scheme == "https" and url.hostname == "ted.europa.eu"
    country = record.get("country") in ("DE", "DEU")
    if project and trades and cpv and text and source and country and confidence >= .70:
        status = "CONFIDENT"
    elif project or trades:
        status = "REVIEW"
    else:
        status = "UNKNOWN"
    return status, {"project_type": project, "trade": trades, "cpv": cpv,
        "textual_evidence": int(text), "source": source, "country": country,
        "confidence": round(confidence, 3), "policy_version": POLICY_VERSION}
