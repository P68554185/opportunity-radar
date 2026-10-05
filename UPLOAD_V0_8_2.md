# Opportunity Radar v0.8.2 — Stable Workflow

Einmalig muss `.github/workflows/live-ingestion.yml` aus diesem Paket in GitHub aktualisiert werden.

Danach bleibt der GitHub-Workflow stabil. Zukünftige Versionen ändern nur noch
`run_pipeline.py` und normale sichtbare Repository-Dateien. Damit reicht künftig
der normale Komplett-Upload ins Repository-Root.

Nach dem Upload:
1. Commit durchführen.
2. Actions > Live Data Ingestion > Run workflow.
3. Im Log erscheint nur noch ein Workflow-Schritt "Run Opportunity Radar pipeline";
   darin werden die einzelnen Pipeline-Stufen mit Überschriften protokolliert.
