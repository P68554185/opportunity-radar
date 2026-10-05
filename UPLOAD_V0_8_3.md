
# Opportunity Radar v0.8.3 — Quality Validation

## Neu
- konservatives Quality Gate: CONFIDENT / REVIEW / UNKNOWN
- schwache Klassifikationen werden nicht als belastbare Kunden-Opportunity behandelt
- reproduzierbare 60er Audit-Stichprobe
- CSV mit Originaltext, CPV, Vorhersage, Confidence und Evidenz
- Review-Felder bleiben leer, damit keine Accuracy erfunden wird
- Precision / False-Positive-Rate werden erst nach echten Review-Labels berechnet
- stabiler GitHub Workflow bleibt unverändert; neue Logik läuft über run_pipeline.py

## Upload
Gesamten entpackten Ordnerinhalt in das Repository-Root hochladen und vorhandene Dateien ersetzen.
Danach Actions > Live Data Ingestion > Run workflow.

Im Pipeline-Log muss erscheinen:
`=== Validate quality and build audit sample ===`

Erzeugte Dateien:
- reports/quality_validation_summary.json
- reports/quality_audit_sample.csv
- docs/data/quality_validation.json
