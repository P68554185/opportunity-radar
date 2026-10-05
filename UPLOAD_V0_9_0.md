# Opportunity Radar v0.9.0 – Upload

1. ZIP entpacken.
2. Den **Inhalt** des Ordners in das Root-Verzeichnis des GitHub-Repositories `opportunity-radar` hochladen und vorhandene Dateien ersetzen.
3. Committen.
4. GitHub → Actions → **Live Data Ingestion** → **Run workflow**.
5. Nach erfolgreichem Lauf GitHub Pages neu laden (ggf. Strg+F5).

## Neu in v0.9.0
- Smart Validation statt blindem 60-Fälle-Durchklicken.
- Risk-first: verdächtige/widersprüchliche Fälle zuerst.
- Automatische Hinweise zu fehlendem Textbeleg, alternativen Projektarten, nicht belegten Gewerken und generischen Beschreibungen.
- Bestehende Browser-Bewertungen bleiben erhalten.
- Keine Precision ohne echte menschliche Labels.
