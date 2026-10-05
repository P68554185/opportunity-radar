# Bestandsaufnahme und Zielarchitektur
## Vorhanden
Python-Kern (engine.py), regelbasierte Klassifikation, TED-Suche über urllib, normalisierte/enriched JSON-Snapshots, kuratierte bayerische Fördermeldungen, Lifecycle-Heuristiken und SQLite-Entwicklungsdatenbank.
GitHub Actions führt tägliche TED-Akquisition aus und committet generierte Daten. GitHub Pages veröffentlicht docs/.
PostgreSQL-Schema ist eine Vorlage; keine laufende Datenbank, Authentifizierung, Kunden-API, E-Mail- oder Zahlungsintegration wurde im Repository nachgewiesen.
Es gibt mehrere historische Adapter/Upload-Kopien und Bytecode-Dateien. Sie bleiben vorerst erhalten; aktive Pipeline ist run_pipeline.py.

## Aktiver Datenweg
TED → live/normalize.py → intelligence/build.py → gemeinsame intelligence/evidence.py → quality gate → Audit/CONFIDENT-Kundenfeed → intelligence/customer_feed.py → BauRadar-Darstellung.
37 kuratierte EARLY-Events → engine.ingest → konservative Masterprojekte → offizielle Quellenprüfung → frühe Projektkarten mit ausdrücklich möglichen Gewerken.
Unbekannte Ausschreibungszeiten bleiben null. Zukünftige Zeitprognosen benötigen Beobachtungsdaten und eine separate Validierung.

## Nachweis und Bewertung
classification_confidence: deterministische Belegstärke aus Projekttext und Bau-CPV. Keine statistisch kalibrierte Wahrscheinlichkeit.
opportunity_score: kommerzielle Rangfolge; nicht Teil des Beweisgates.
quality_status: Freigabe-/Review-Entscheidung.
Lifecycle-Kandidaten: Review ist keine bestätigte Identität; Auto-Link benötigt Abstand zum zweitbesten Kandidaten und Titelbeleg.
Ontology-Gewerkwerte im historischen engine.py sind Annahmen, keine gemessene KI-Genauigkeit; die neue Kundenansicht zeigt keine solchen Prozentwerte.

## Deployment
build_snapshot.py erzeugt und prüft vollständige Daten offline vor Pages-Upload.
Pages reagiert zusätzlich auf erfolgreiche Ingestion: mit GITHUB_TOKEN erzeugte Pushes lösen sonst keine nachfolgenden Push-Workflows aus.
CI läuft unabhängig von externen TED-Diensten auf dem committed Snapshot.
Die tägliche Live-Akquisition ersetzt bei Fehlern, unvollständigem Umfang oder Duplikaten den letzten geprüften Snapshot nicht.

## Nächster Infrastruktur-Schritt
Ein Python-Backend mit serverseitiger Persistenz und Session-Login kann den vorhandenen Datenkern wiederverwenden.
Erforderlich: TLS, persistentes Volume/PostgreSQL, Secrets, Backups, Monitoring und geschütztes Admin-Routing.
Ein neuer externer Account oder kostenpflichtiger Host wurde nicht angelegt.
Bis dahin bleiben Betriebsprofile/Merklisten ausschließlich lokal im Browser; keine personenbezogenen Kundendaten in öffentlichen Git-Snapshots.
