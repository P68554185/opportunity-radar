# BauRadar – Entwicklungsstatus
Stand: 05.10.2026. Verbindlich sind geprüfte Funktionen und Actions-Ergebnisse, nicht Zieltermine.

## Meilensteine
| Meilenstein | Stand | Abnahmekriterium |
|---|---|---|
| Bestandsaufnahme | abgeschlossen | Architektur, Quellen, Pipeline, Workflows und Grenzen dokumentiert |
| Datenmotor / Evidence | CI erfolgreich | Evidenz unabhängig vom kommerziellen Score; keine leeren CPV als Beleg |
| Lifecycle / Persistenz | erste vollständige CI erfolgreich | Widersprüche blockiert; mehrdeutige Links bleiben Review; Historie bleibt bei Folgeläufen erhalten |
| Kundenoberfläche | Chromium-Abnahme erfolgreich | Deutsche Begriffe, Originalquelle, Phase, Gewerk, Auftraggeber, nächste Handlung |
| Betriebsprofil / Beobachten | lokale MVP-Vorschau | Ort und Gewerke filtern; Merkliste über Browser-Neustart erhalten |
| Radius / Entfernung | offen | Geprüfte Koordinaten und geographische Abdeckung nötig |
| Anmeldung / serverseitige Profile | implementiert und getestet; Deployment blockiert | Backend-Host fehlt (vom Nutzer bestätigt) |
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
- Admin-Vorlage liegt außerhalb des Pages-Verzeichnisses; ein produktiv gehosteter Admin-Server fehlt noch.
- Öffentliche Quelldaten und Audits enthalten keine Zugangsdaten; spätere Kundendaten dürfen dort nicht gespeichert werden.
- Geprüfter Kundendatensatz bedeutet Evidence-Screening, keine fachlich gemessene Precision.

## Nächste Schritte
1. Kostenlose Render-/Neon-Accounts sicher anbinden und das geprüfte Backend als Kundenvalidierungs-Pilot bereitstellen.
2. Backend-Infrastruktur auswählen und bereitstellen; erst anschließend Login und serverseitige Profile anbinden.
3. Geodatenquelle und kommerzielle Nutzungsbedingungen klären; Radius mit unbekannten Orten konservativ behandeln.
4. Laufende EARLY-Akquisition aus weiteren offiziellen Quellen und manuell bewerteten Stichproben ausbauen.
5. E-Mail, Tarife/Zahlung und rechtliche Texte mit erforderlichen Nutzerentscheidungen anschließen.

## Ergebnis der vollständigen Quellenprüfung
2.000 gespeicherte Quellzeilen enthalten 29 doppelte TED-IDs. Nach Bereinigung bleiben 1.971 eindeutige Meldungen, davon 655 CONFIDENT, 1.250 REVIEW und 66 UNKNOWN nach der neuen Belegpolitik. 37 EARLY-Meldungen ergeben konservativ 36 Masterprojekte. Kundenfeed: 691 Einträge (655 TED, 36 frühe Projekte). Ein Lifecycle-Kandidat bleibt Review; null automatisch bestätigte Verbindungen. Dies wurde im erfolgreichen CI-Lauf 37328438780 nachgewiesen.

## Backend-Vorbereitung
Session-Login, serverseitige Betriebsprofile und Merklisten sowie geschütztes Admin-Routing sind implementiert. Die Oberfläche nutzt sie automatisch, sobald der Backend-Host verfügbar ist. Das ist noch kein produktives Login auf GitHub Pages. Die Container-/Betriebskonfiguration steht in backend/README.md; öffentliche Registrierung ist standardmäßig deaktiviert. End-to-End-Abnahme in Chromium erfolgreich (Desktop, Mobil, Filter, lokale Merkliste, Registrierung/Logout, serverseitiges Profil und Merkliste). E-Mail-Verifikation/Passwort-Reset, E-Mail-Versand, Zahlung und Hosting bleiben offen.

## Validierung und Bereitstellungsvorschlag
CI-Läufe 37331459564 und 37331452274 bestanden für Commit 480c674a1490a373f6586309b8a4fcd445d41087. 17 Kern-/Evidenz-/Akquisitions-/Phasentests, bestehender Pipeline-Smoke-Test, 8 Classifier-Fälle, 6 Account-Tests und Chromium-End-to-End-Abläufe wurden erfolgreich ausgeführt. Die neue Container-/TLS-Vorlage und ein konsistentes privates SQLite-Backup werden zusätzlich geprüft. Hostingentscheidung und reale Server-/Domain-Zugangsdaten fehlen. Keine öffentliche Kontoregistrierung wird ohne diese Abnahme freigeschaltet.

## Abschließende technische Abnahme
CI 37332039989 / 37332032772 für Commit 02dd1036e978bbf426bac490d211fe2215069c38: Kern, vollständiger Feed, 7 Backend-/Backup-Tests, Chromium-Abläufe, Docker-Compose-Konfiguration und Container-Build erfolgreich. Konsistentes Datenbankbackup konnte aus einer privaten Datei wieder gelesen werden. Produktions-Smoke-Workflow prüft nach Pages-Veröffentlichung die echte URL sowie Filter, lokale Persistenz und mobile Darstellung. Der produktive Backend-Host bleibt ein externer Blocker.

## Aktueller Live-Stand nach Integration
PR #1 wurde in main integriert. Live-Akquisition 37333090288 erfolgreich, Pages-Deployment 37333152494 erfolgreich.
Der neue Lauf am 05.10.2026 um 15:28 UTC verarbeitet **2.000 eindeutige TED-Meldungen**; 66 überlappende Treffer wurden während der Akquisition übersprungen und durch weitere Seiten ersetzt.
Aktuelle Evidenzprüfung: **658 CONFIDENT, 1.272 REVIEW, 70 UNKNOWN**. **37 EARLY-Meldungen / 36 Masterprojekte**. Aktueller Kundenfeed: **694 Einträge** (658 TED, 36 frühe Projekte).
Nach der Korrektur der Klassifikation ohne Auftraggebernamen liefert der aktuelle Live-Stand **0 Lifecycle-Kandidaten / 0 bestätigte Auto-Links**. Der eine Kandidat des historischen Snapshots ist kein fortgeschriebener Nachweis.
Der Browser-Test der veröffentlichten URL bestätigt 694 Kundenprojekte, Gewerkfilter, lokale Persistenz und mobile Darstellung. Run-Logs enthalten den tatsächlichen URL-Test, nicht nur einen erfolgreichen Upload.

Veröffentlicht: https://p68554185.github.io/opportunity-radar/
Produktionsvorschlag: deploy/README.md (Docker, TLS-Proxy, persistentes Volume; Containerbuild und Konfiguration geprüft).
**Nächster externer Blocker: kostenlose Render-/Neon-Accounts und sichere Konfiguration der Datenbankverbindung.** Rechtliche Texte und anschließend E-Mail-/Zahlungsaccounts bleiben erforderlich.
Die laufende Vorschau ist nutzbar; eine verkaufsfähige SaaS-GO-LIVE-Freigabe wird noch nicht behauptet.

## Verbindliche Kostenentscheidung des Nutzers
Kostenpflichtiges Hosting erst nach erfolgreicher Kundenvalidierung. Bis dahin keine kostenpflichtigen Hostingbestellungen.
GitHub Pages bleibt die laufende kostenlose Vorschau. Ein kostenloser Konto-Pilot ist für Render Free + Neon Free vorbereitet; eine gekaufte Domain ist dafür nicht nötig.
Das vorhandene Backend unterstützt PostgreSQL zusätzlich zu SQLite. Auf flüchtigen Render-Hosts verhindert es den Start ohne dauerhafte PostgreSQL-Konfiguration/TLS.
Konto-, Sitzungs-, Neustart- und Merkliste-Isolationstests bestehen gegen SQLite und PostgreSQL 16 (CI 37334583300). Plattform-Healthchecks wecken die Datenbank nicht dauerhaft.
Render- und Neon-Nutzungslimits/Ruhephasen bleiben Einschränkungen eines Kundenvalidierungs-Pilots. Kein kostenpflichtiger Tarif und kein neuer externer Account wurde eingerichtet.
Konkrete Einrichtung, Grenzen und sichere Secret-Konfiguration: deploy/FREE_PILOT.md. Die Accounts fehlen noch; der kostenlose Backend-Pilot ist noch nicht deployt.
