# Opportunity Radar v0.7.3 – FULL UPLOAD

Dies ist ein vollständiger Repository-Build, kein Patch.

## Upload-Regel ab v0.7.3
1. Diesen Ordner entpacken.
2. Den **gesamten Inhalt** dieses Ordners in das Root des GitHub-Repositories hochladen.
3. GitHub vorhandene gleichnamige Dateien ersetzen lassen.
4. Commit: `Opportunity Radar v0.7.3 full upload`.
5. Danach `Actions -> Live Data Ingestion -> Run workflow`.

Wichtig: Nicht den äußeren Ordner als zusätzlichen Unterordner hochladen. In GitHub müssen `.github`, `adapters`, `benchmarks`, `classification`, `docs`, `lifecycle`, `live`, `real_data`, `reports`, `review`, `sql`, `tests` direkt im Repository-Root liegen.

v0.7.3 enthält den zuvor fehlenden `live/normalize.py` und alle abhängigen Module aus dem vollständigen Build.
