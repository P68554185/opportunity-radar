# Opportunity Radar v0.7.2 – Live TED Update

Enthaltene Änderungen:
- live/ted_fetch.py
- benchmarks/live_ted_500.py
- github_status.py
- workflow_upload/live-ingestion.yml

GitHub-Upload:
1. `live/ted_fetch.py` ersetzt die gleichnamige Datei im Repository.
2. `benchmarks/live_ted_500.py` ersetzt die gleichnamige Datei.
3. `github_status.py` ersetzt die Datei im Repository-Root.
4. In GitHub `.github/workflows` öffnen und dort `workflow_upload/live-ingestion.yml` hochladen.
   Die Datei muss am Ende unter `.github/workflows/live-ingestion.yml` liegen.
5. Danach Actions -> Live Data Ingestion -> Run workflow.

Der Workflow ruft bis zu 500 TED-Bauvergaben über die öffentliche TED Search API v3 ab.
Bei einem echten Abruffehler wird kein leerer Datensatz als erfolgreicher Sync veröffentlicht.
