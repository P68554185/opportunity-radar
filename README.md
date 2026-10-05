# BauRadar / Opportunity Radar
Ein einfaches Auftragsfrühwarnsystem für deutsche Bauunternehmen und Handwerker.
Die aktuelle GitHub-Pages-Version ist eine MVP-Vorschau mit offiziellen Bauprojektquellen, Gewerk-/Ortsfilter und lokaler Merkliste. Login, Umkreissuche, E-Mail und Bezahlung sind noch nicht produktiv verfügbar.

- [Entwicklungsstatus und Roadmap](DEVELOPMENT_STATUS.md)
- [Bestandsaufnahme und Architektur](ARCHITECTURE.md)
- [Kundenoberfläche](https://p68554185.github.io/opportunity-radar/)

## Datenqualität
Classification Rate beschreibt den Anteil klassifizierter Meldungen, keine Accuracy.
Classification-Confidence ist regelbasierte Belegstärke und unabhängig vom kommerziellen Opportunity Score.
Der TED-Kundenfeed enthält ausschließlich Einträge aus der gemeinsamen Evidenzprüfung.
Frühe Projekte stammen aus offiziellen Fördermeldungen; mögliche Gewerke sind als Ableitung aus der Projektart gekennzeichnet.
Lifecycle-Kandidaten und unbekannte Vergabezeiträume werden nicht als bestätigte Verbindungen oder Termine ausgegeben.

## Ausführen
Python 3.12, für die aktive Pipeline keine externen Pakete nötig.

```sh
python -m unittest discover -s tests -p 'test_*.py'
python benchmarks/classifier_regression.py
python build_snapshot.py
```

Der Snapshot-Build verwendet gespeicherte echte Daten ohne Netzwerkzugriff.
`python run_pipeline.py` führt zusätzlich die Live-TED-Akquisition aus.
GitHub Actions: **Verify BauRadar**, **Live Data Ingestion**, **Deploy Website**.
Die technische Prüfansicht liegt als Vorlage unter `admin/` außerhalb des veröffentlichten Pages-Verzeichnisses.
