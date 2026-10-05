# Opportunity Radar v0.8.3

Stable GitHub workflow architecture.

# Opportunity Radar v0.8.1 — Live Intelligence

v0.8.1 converts the proven TED live acquisition into an intelligence pipeline:

`TED Live → normalize → classify project/trades → opportunity score → EARLY lifecycle candidates → dashboard feed`

## New in v0.8.1
- Broad construction ontology: 16+ project types and 19+ trade/service classes.
- CPV-prefix classification as fallback for terse TED titles.
- Live Opportunity builder and confidence band (`HOT`, `UPCOMING`, `EARLY`).
- Candidate matching between verified Bavarian EARLY signals and later TED records.
- Dashboard Opportunity Feed generated from real live records.
- GitHub Action runs regression → 500 live TED notices → intelligence → dashboard update.

## Data integrity
- No synthetic fallback in the live workflow.
- `500 downloaded_live` means 500 records returned by TED in that run.
- `classified_opportunities` is a deterministic subset of live records, not a prediction accuracy claim.
- `lifecycle_candidates` are candidate links; only high-confidence candidates are marked `auto_link`, others remain review candidates.

## Run
Use GitHub Actions → **Live Data Ingestion** → **Run workflow**.


## v0.8.1
Adds automated opportunity quality analytics and dashboard QA views before scaling ingestion volume.

## v0.8.7
Adds an enriched full-dataset layer (`real_data/ted_live_enriched.json`) between classification and the quality gate. It carries project type, trades, CPV, confidence/score and evidence into quality screening so the gate evaluates the intelligence output rather than raw normalized notices.


## v0.8.7
Quality Audit UI auf GitHub Pages für 60 stratifizierte Fälle. Browser-lokale Review-Labels, Live-Precision nur aus echten Bewertungen und CSV-Export.
