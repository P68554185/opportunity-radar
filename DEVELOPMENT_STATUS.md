# BauRadar – Entwicklungsstatus
Stand: 05.10.2026. Verbindlich sind geprüfte Funktionen und Actions-Ergebnisse, nicht Zieltermine.

## Meilensteine
| Meilenstein | Stand | Abnahmekriterium |
|---|---|---|
| Bestandsaufnahme | abgeschlossen | Architektur, Quellen, Pipeline, Workflows und Grenzen dokumentiert |
| Datenmotor / Evidence | umgesetzt, CI läuft | Evidenz unabhängig vom kommerziellen Score; keine leeren CPV als Beleg |
| Lifecycle / Persistenz | umgesetzt, CI läuft | Widersprüche blockiert; mehrdeutige Links bleiben Review; Historie bleibt bei Folgeläufen erhalten |
| Kundenoberfläche | umgesetzt, CI läuft | Deutsche Begriffe, Originalquelle, Phase, Gewerk, Auftraggeber, nächste Handlung |
| Betriebsprofil / Beobachten | lokale MVP-Vorschau | Ort und Gewerke filtern; Merkliste über Browser-Neustart erhalten |
| Radius / Entfernung | offen | Geprüfte Koordinaten und geographische Abdeckung nötig |
| Anmeldung / serverseitige Profile | blockiert | Backend-Host fehlt (vom Nutzer bestätigt) |
| Benachrichtigungen / E-Mail | offen | Persistenz, Versandaccount, verifizierte Absenderdomain, Opt-in |
| Tarife / Zahlung | offen | Preisstrategie und Zahlungsaccount; keine kostenpflichtigen Dienste angelegt |
| Verkaufsfähiger Produktionsbetrieb | nicht erreicht | Zugangsschutz, Backups, Betrieb, Datenschutz/Impressum, Zahlung und End-to-End-Abnahme |

## Verifizierter Ausgangsstand
Gespeicherte Berichte: 2.000 TED-Records, 1.937 klassifizierte Records, 1.124 CONFIDENT, 813 REVIEW, 63 UNKNOWN.
Die EARLY-Quelldatei enthält 37 Meldungen. Die Zahl 34 Masterprojekte und die 488 zusätzlichen Opportunities waren im Statusgenerator fest codiert; deshalb sind diese alten Zähler kein unabhängiger Nachweis.
Ein Lifecycle-Kandidat ist keine bestätigte Projektverbindung.
Die letzten vorgefundenen Live-Ingestion- und Pages-Läufe waren erfolgreich.
Vollständige Datensatzprüfung erfolgt durch den neuen CI-Snapshot: aktuelle Zahlen können durch die strengere Beweispolitik sinken.

## Änderungen
- Eine gemeinsame Evidenzpolitik für Gate und Kundenfeed; Classification-Confidence ist regelbasierte Belegstärke, keine gemessene Accuracy.
- Keine kommerziellen Scores als Ersatz für fehlende Klassifikationsbelege.
- CPV-Format, Bau-CPV, Originalquelle und Deutschland-Bezug werden geprüft.
- Klassifikation nutzt Projekttext und CPV; der Auftraggebername ist kein Nachweis für die Projektart.
- Ambiguitätsabstand und Titelbeleg schützen Lifecycle-Verknüpfungen.
- SQLite-Folgeläufe übernehmen vorhandene Projekte und Ereignishistorie.
- Statuszähler werden aus Quelldaten und generiertem Kundenfeed abgeleitet.
- Unvollständige oder doppelte TED-Akquisition ersetzt den letzten geprüften Datensatz nicht.
- Pages baut einen vollständigen geprüften Snapshot; nach erfolgreicher Ingestion wird Pages explizit ausgelöst.
- Kein erfundener Ausschreibungszeitraum, keine Genauigkeitsprozente in der Kundenansicht.

## Bekannte Grenzen
- EARLY-Quellen: kuratierte bayerische Fördermeldungen, keine flächendeckende laufende Frühprojekt-Akquisition.
- TED-CPV-45-Suche deckt Bauvergaben ab; gesonderte Planungsvergaben sind damit nicht vollständig erfasst.
- Projektzusammenführung ist konservativ; gleiche Gebäude mit verschiedenen Titeln können getrennt bleiben.
- Lokale Profile/Merklisten sind gerätegebunden und senden keine Benachrichtigungen.
- Admin-Vorlage liegt außerhalb des Pages-Verzeichnisses; ein geschützter Admin-Server fehlt noch.
- Öffentliche Quelldaten und Audits enthalten keine Zugangsdaten; spätere Kundendaten dürfen dort nicht gespeichert werden.
- Geprüfter Kundendatensatz bedeutet Evidence-Screening, keine fachlich gemessene Precision.

## Nächste Schritte
1. CI abschließen, Fehler beheben, geprüfte Änderung integrieren und Pages-Deployment abnehmen.
2. Backend-Infrastruktur auswählen und bereitstellen; erst anschließend Login und serverseitige Profile anbinden.
3. Geodatenquelle und kommerzielle Nutzungsbedingungen klären; Radius mit unbekannten Orten konservativ behandeln.
4. Laufende EARLY-Akquisition aus weiteren offiziellen Quellen und manuell bewerteten Stichproben ausbauen.
5. E-Mail, Tarife/Zahlung und rechtliche Texte mit erforderlichen Nutzerentscheidungen anschließen.
