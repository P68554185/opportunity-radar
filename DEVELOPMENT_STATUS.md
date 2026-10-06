# BauRadar – Entwicklungsstatus
Stand: 06.10.2026. Funktionsnachweise haben Vorrang vor Zielterminen.

## Meilensteine
| Meilenstein | Stand | Nächster Nachweis / offene Arbeit |
|---|---|---|
| Bestandsaufnahme / Architektur | abgeschlossen | ARCHITECTURE.md |
| Datenmotor / Evidenz | integriert und geprüft | Evidenz und kommerzieller Score getrennt; Dubletten und widersprüchliche Links blockiert |
| EARLY / Lifecycle | konservative Engine vorhanden | 37 kuratierte Signale / 36 Masterprojekte; laufende breitere Akquisition fehlt |
| Einfache Kundenoberfläche | veröffentlicht, Chromium geprüft | Quelle, Gewerk, Phase, Auftraggeber, nächste Handlung |
| Kostenloses Backend | Render + Neon eingerichtet | Live-Check 37429224942 erfolgreich: Datenbank erreichbar, 690 geprüfte Feed-Einträge |
| Betriebsprofile / Merkliste / Login | implementiert, SQLite/PostgreSQL und Browser geprüft | Registrierung öffentlich deaktiviert; kein live getestetes Kundenkonto |
| Prozessneustart / Kontotrennung | zusätzliche Tests in Arbeit | Echter Neustart mit PostgreSQL; zwei Konten im Browser |
| Automatischer Render-Feed | Umsetzung in Arbeit | Geprüfte Pages-Daten per Servercache übernehmen, ohne täglichen Redeploy |
| Entfernung / Radius | offen | geprüfte Koordinaten und geographische Abdeckung |
| E-Mail / Benachrichtigungen | offen | Verifizierung, Passwort-Reset, Versand und Opt-in |
| Tarife / Bezahlung | offen | Nutzerentscheidung über Angebot/Preis und Zahlungsweg |
| Verkaufsfähiger Betrieb | nicht erreicht | Rechtstexte, Backup/Wiederherstellung, Live-Kontotests und Kundenpilot |

## Laufende Systeme
- Vorschau: https://p68554185.github.io/opportunity-radar/
- Konto-Pilot: https://bauradar-pilot.onrender.com/
- Nutzer hat Render/Neon über GitHub eingerichtet; Datenbankverbindung ausschließlich im Host hinterlegt.
- Live-Prüfung am 06.10.2026: HTTPS-Seite, Backend, Datenbank/Schemaanlage, qualifizierter Feed und anonymer Zugriffsschutz erfolgreich.
- Registrierung, E-Mail und Zahlung deaktiviert. Die Admin-E-Mail-Allowlist legt kein Konto an.
- Die GitHub-Anbindung der Anbieter verschafft dem Assistenten keinen Dashboard-/Redeploy-Zugriff.

## Datenqualität
Keine gemessene Accuracy wird behauptet. Classification-Confidence ist regelbasierte Belegstärke; die Klassifikationsquote ist keine Accuracy.
Der Kundenfeed enthält ausschließlich CONFIDENT-TED und offiziell verifizierte EARLY-Projekte.
Frühe Gewerke sind aus der Projektart abgeleitet; unbekannte Ausschreibungszeiträume bleiben unbekannt.
37 EARLY-Signale sind kuratiert und überwiegend bayerische Fördermeldungen; noch keine bundesweite laufende Frühprojektabdeckung.
Live-Datenzahlen ändern sich mit erfolgreichen Pipeline-Läufen. Der Render-Live-Check ermittelte 690 Einträge am 06.10.2026; dies ist kein dauerhaft festgelegter Zähler.
Konservative Lifecycle-Verknüpfungen sind keine Garantie vollständiger Gebäudezusammenführung.

## Nächste Schritte
1. Automatische Feed-Übernahme und zusätzliche PostgreSQL-/Browser-Kontotests integrieren und CI abnehmen.
2. Neue Backend-Version auf Render veröffentlichen und Live-Feed prüfen; manueller Nutzer-Redeploy erforderlich, solange kein sicherer Anbieterzugriff besteht.
3. Geschlossenen Kontotest vorbereiten; keine öffentliche Registrierung vor Infrastruktur-/Datenschutz-Abnahme.
4. PostgreSQL-Backup/Wiederherstellung und persistente Konten über echten Render-Redeploy prüfen.
5. Radius, weitere EARLY-Quellen, E-Mail sowie Angebot/Rechtstexte vervollständigen.

## Verbindliche Kostenentscheidung
Kostenpflichtiges Hosting erst nach erfolgreicher Kundenvalidierung. Keine kostenpflichtigen Hostingbestellungen oder automatischen Upgrades.
Render Free und Neon Free haben Ruhephasen und Nutzungslimits; kein Produktions-SLA zugesichert.
Einrichtung und Nachweise: deploy/FREE_PILOT.md.

## Bereits integrierte Entwicklung
PRs #1–#4: Datenmotor, Evidenzpolitik, Dublettenbereinigung, konservative Lifecycle-Regeln, einfache UI, Konto-Backend,
PostgreSQL/TLS-Unterstützung, korrigierte CPV-Gewerke und phasengerechte nächste Handlung.
Kern-, Feed-, SQLite-/PostgreSQL-, Browser- und Dockerprüfungen bestanden vor Integration.
GitHub Actions veröffentlicht Pages nach erfolgreicher Live-Ingestion. Admin liegt außerhalb des öffentlichen Pages-Verzeichnisses.
Kundendaten und Zugangsdaten dürfen nicht in Git, Artefakte oder öffentliche Logs gelangen.
