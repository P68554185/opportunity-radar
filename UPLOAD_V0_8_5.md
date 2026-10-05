# Opportunity Radar v0.8.5 — Enriched Quality Pipeline

Upload the complete contents of this folder to the repository root and replace existing files.

Then run **Actions → Live Data Ingestion → Run workflow**.

Expected log section `=== Full dataset quality gate ===`:
- `source`: `real_data/ted_live_enriched.json`
- `records_seen`: 500
- `gate_total_matches_records`: true
- the 500 records should be distributed across CONFIDENT / REVIEW / UNKNOWN instead of all UNKNOWN.

v0.8.5 does not claim measured accuracy. The quality gate remains evidence screening until the audit sample has human labels.
