# BauRadar – Entwicklungsstatus
Stand: 06.10.2026. Funktionsnachweise haben Vorrang vor Zielterminen.

## Aktiver Entwicklungsblock: EARLY / Lifecycle

Baseline geprüft am 06.10.2026: 2.000 eindeutige TED-Meldungen, 1.926 klassifizierte Chancen,
654 qualifizierte TED-Einträge; 37 EARLY-Signale / 36 Masterprojekte, 690 Kundenkarten.
Kein bestätigter Link im bisherigen laufenden Datenbestand.
Alle letzten vollständigen CI-, Pages- und Render-Prüfungen erfolgreich.

In Arbeit: erklärbare Identitätsprüfung und reproduzierbarer historischer Rückblick
mit echten gespeicherten TED-Meldungen. Die historischen Beispiele wurden erst jetzt
recherchiert; ihre Zeitabstände sind kein live erzielter BauRadar-Vorsprung.
Offen: laufende breitere EARLY-Akquisition, Master-/Feed-Integration, mobile Historie,
unabhängig bewertete Validierungsmenge und Veröffentlichung/Live-Abnahme.
Keine Erhöhung des Gesamtfortschritts allein aufgrund recherchierter Beispiele.
Details: [EARLY-/Lifecycle-Ledger](docs-internal/EARLY_LIFECYCLE.md).

## Meilensteine
| Meilenstein | Stand | Nächster Nachweis / offene Arbeit |
|---|---|---|
| Bestandsaufnahme / Architektur | abgeschlossen | ARCHITECTURE.md |
| Datenmotor / Evidenz | integriert und geprüft | Evidenz und kommerzieller Score getrennt; Dubletten und widersprüchliche Links blockiert |
| EARLY / Lifecycle | konservative Engine vorhanden | 37 kuratierte Signale / 36 Masterprojekte; laufende breitere Akquisition fehlt |
| Einfache Kundenoberfläche | veröffentlicht, Chromium geprüft | Quelle, Gewerk, Phase, Auftraggeber, nächste Handlung |
| Kostenloses Backend | Render + Neon eingerichtet | Live-Check 37429224942 erfolgreich: Datenbank erreichbar, 690 geprüfte Feed-Einträge |
| Geschlossener Kontotest | Live-Test auf Render/Neon erfolgreich | 37435166258, Versuch 3: zwei Konten, Profile/Merklisten, Logout/Login, Secure-Cookies; Redeploy-Persistenz erfolgreich (37436725262) |
| Betriebsprofile / Merkliste / Login | implementiert, SQLite/PostgreSQL und Browser geprüft | Registrierung öffentlich deaktiviert; zwei synthetische Konten live geprüft |
| Prozessneustart / Kontotrennung | CI erfolgreich | Echter Neustart mit PostgreSQL; zwei Konten im Browser; CI 37431562638 |
| Automatischer Render-Feed | auf Render veröffentlicht und live geprüft | Geprüfte Pages-Daten per Servercache übernehmen, ohne täglichen Redeploy |
| PostgreSQL-Sicherung / Restore | Werkzeuge integriert; Wiederherstellung in CI erfolgreich | Produktive Sicherungsplanung und verschlüsselte Ablage offen |
| Bereinigung des Testzugangs | Betreiber bestätigt; öffentliche Live-Prüfung bestanden | Secret in Render/GitHub entfernt; Konto-Löschung beim Neustart in CI geprüft, nicht separat live ausgelesen |
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
1. Laufende EARLY-Akquisition und bewertete Stichproben aus weiteren offiziellen Quellen ausbauen.
2. Standort-/Radiusabdeckung mit geprüften Koordinaten und geklärten Nutzungsbedingungen vervollständigen.
3. Geschlossene Kundenaufnahme, E-Mail-Verifizierung/Passwort-Reset und Benachrichtigungen ergänzen.
4. Produktive Sicherungsplanung und verschlüsselte Ablage einrichten; CI-Backup/Restore bereits bestanden.
5. Angebot/Preis, Bezahlweg und Rechtstexte mit den erforderlichen Betreiberentscheidungen abschließen.

## Verbindliche Kostenentscheidung
Kostenpflichtiges Hosting erst nach erfolgreicher Kundenvalidierung. Keine kostenpflichtigen Hostingbestellungen oder automatischen Upgrades.
Render Free und Neon Free haben Ruhephasen und Nutzungslimits; kein Produktions-SLA zugesichert.
Einrichtung und Nachweise: deploy/FREE_PILOT.md.

## Bereits integrierte Entwicklung
PRs #1–#7: Datenmotor, Evidenzpolitik, Dublettenbereinigung, konservative Lifecycle-Regeln, einfache UI, Konto-Backend,
PostgreSQL/TLS-Unterstützung, korrigierte CPV-Gewerke und phasengerechte nächste Handlung.
Kern-, Feed-, SQLite-/PostgreSQL-, Browser- und Dockerprüfungen bestanden vor Integration.
GitHub Actions veröffentlicht Pages nach erfolgreicher Live-Ingestion. Admin liegt außerhalb des öffentlichen Pages-Verzeichnisses.
Kundendaten und Zugangsdaten dürfen nicht in Git, Artefakte oder öffentliche Logs gelangen.

## Abnahme PR #5
https://github.com/P68554185/opportunity-radar/pull/5 — integriert am 06.10.2026.
https://github.com/P68554185/opportunity-radar/actions/runs/37431562638 — vollständige Prüfung erfolgreich.
Neue Tests: Feed-Rückfall/Validierung, tatsächlicher PostgreSQL-Prozessneustart mit deaktivierter Registrierung nach Neustart, erneuter Login und zweites unabhängiges Browserkonto. Docker-Build erfolgreich.
Render-Redeploy dieser Version erfolgreich; noch kein Kontotest gegen die echte Neon-Datenbank. Keine öffentliche Registrierung freigeschaltet.

## Render-Abnahme nach manuellem Deployment
06.10.2026, 09:49 Uhr Europe/Berlin: Live-Check 37432113469 erfolgreich. Dynamische Feed-Route (Cache-Control no-store) ist veröffentlicht; Render-Datenstand entspricht der veröffentlichten Pipeline (2026-10-06 05:25 UTC, 690 Projekte). Backend, Datenbank und anonymer Zugriffsschutz erfolgreich; Registrierung bleibt deaktiviert.
Nächster externer Schritt: geschlossener Kontotest ohne öffentliche Registrierung, danach echter Render-Redeploy mit Konto-Persistenzprüfung. Wiederherstellung, Rechtstexte und E-Mail bleiben offen.

## PostgreSQL-Sicherung: technische Abnahme bestanden
Privates pg_dump-Custom-Archiv außerhalb des Repositorys mit Dateirechten 0600; keine Verbindungspasswörter in Prozessargumenten oder Logs. Restore blockiert Quell- und befüllte Zieldatenbanken. CI prüft Wiederherstellung von Konten, Profilen, Sitzungen und Merklisten in getrennten Wegwerf-Datenbanken.
Produktive Backup-Zeitplanung, verschlüsselte externe Ablage und ein Restore der echten Neon-Datenbank sind noch nicht eingerichtet.

PR #6 integriert: https://github.com/P68554185/opportunity-radar/pull/6
Vollständige CI erfolgreich: https://github.com/P68554185/opportunity-radar/actions/runs/37432784843
Tatsächlicher Dump/Restore gegen getrennte PostgreSQL-16-Datenbanken; Konten/Profile/Sitzungen/Merklisten identisch, überschreibende und nichtleere Restore-Ziele blockiert. Anschließende Browser- und Dockerprüfungen erfolgreich. Anleitung: deploy/POSTGRES_RECOVERY.md.
Keine echte Neon-Sicherung angelegt; keine produktive Wiederherstellung vorgenommen. Der nächste Backend-Funktionsschritt bleibt ein geschlossener Kontotest ohne öffentliche Registrierung.

## Geschlossener Kontotest: CI-Ergebnis und Live-Blocker
PR #7 integriert: https://github.com/P68554185/opportunity-radar/pull/7
Vollständige CI erfolgreich: https://github.com/P68554185/opportunity-radar/actions/runs/37433704129
Chromium gegen PostgreSQL bei BAURADAR_ENABLE_SIGNUP=false: zwei vorhandene synthetische Konten, Profil-/Merkliste-Isolation, Logout/Wiederanmeldung, tatsächlicher Prozessneustart mit vorhandenen Sitzungen und automatische Bereinigung nach Entfernen des Test-Secrets bestanden. Testkonten erhalten keine Adminrechte.
CI verwendet lokales HTTP (Secure-Cookies dort deaktiviert); das ist ausdrücklich kein HTTPS-/Render-/Neon-Kontotest. Der Live-Workflow prüft HTTPS-Cookies separat, sobald der Betreiber denselben zufälligen BAURADAR_CLOSED_TEST_PASSWORD-Wert sicher in Render und GitHub gesetzt und main deployt hat. Eine weitere Live-Prüfung nach manuellem Render-Redeploy erfolgt mit verify_persistence=true, ohne die bestehenden Testprofile zuerst zurückzusetzen.
Öffentliche Registrierung bleibt deaktiviert; keine Live-Testkonten wurden durch den Assistenten angelegt. Einrichtung/Bereinigung: deploy/CLOSED_ACCOUNT_TEST.md.

## Erster geschlossener Live-Test: Anmeldung blockiert
06.10.2026: Live-Workflow 37435166258 wurde vom Nutzer gestartet und nach Ergänzung reiner HTTP-Status-Diagnostik erneut ausgeführt. Beide Versuche fehlgeschlagen. Die Anwendung ist erreichbar; geschlossenes Signup wird im Preflight geprüft. Anmeldung des ersten synthetischen Kontos liefert HTTP 401. Es ist noch nicht belegt, ob das Fixture-Konto fehlt (Secret-/Deploy-Konfiguration) oder das in GitHub hinterlegte Testpasswort vom Render-Wert abweicht. Sonderzeichen sind im Passwortpfad erlaubt. Kein Passwort/Response-Body wurde geloggt.
Live-Kontotrennung, Live-Profile/Merklisten und Live-Redeploy-Persistenz sind daher noch nicht abgenommen. Nächster Schritt: Betreiber gleicht Render-/GitHub-Testsecret privat ab und prüft das Deployment der Fixture-Version; danach kann der Assistent den fehlgeschlagenen Job erneut starten.

## Geschlossener Live-Kontotest erfolgreich
06.10.2026, 10:25 Uhr Europe/Berlin: https://github.com/P68554185/opportunity-radar/actions/runs/37435166258/attempts/3 erfolgreich.
Zwei synthetische Konten auf echtem Render-/Neon-Pilot in Chromium geprüft: Registrierung geschlossen, Anmeldung, isolierte Profile/Merklisten, Neuladen, Logout und erneute Anmeldung, Admin-Verweigerung, HTTPS-Cookies mit Secure/HttpOnly/SameSite=Strict. Keine Test-Zugangsdaten veröffentlicht.
Die vorherigen HTTP-401-Fehler sind nach Hinterlegung der fehlenden Render-Testvariable behoben.
Noch offen: bestehende Daten nach einem weiteren echten Render-Redeploy im verify_persistence-Modus prüfen. Vor diesem zweiten Test die Test-Secrets beibehalten; erst nach Abschluss entfernen und Cleanup deployen. Keine Aussage über Live-Sitzungserhalt über Redeploy, E-Mail oder Bezahlung.

## Live-Persistenztest erfolgreich
06.10.2026, 10:32 Uhr Europe/Berlin: https://github.com/P68554185/opportunity-radar/actions/runs/37436725262 erfolgreich; VERIFY_PERSISTENCE=true im ausgeführten Job bestätigt.
Bestehende synthetische Profile und Merklisten wurden vor Änderungen geprüft: Konto A behielt sein Profil und genau ein beobachtetes Projekt, Konto B behielt sein getrenntes Profil ohne Merkliste. Anmeldung, Logout/Wiederanmeldung, Admin-Verweigerung und Secure-Cookies ebenfalls erfolgreich.
Dies belegt Profil-/Merkliste-Erhalt nach dem vom Nutzer ausgeführten Render-Redeploy auf der echten Neon-Datenbank. Erhalt bereits offener Live-Sitzungen über Redeploy wurde nicht separat geprüft.
Nächster Schritt: BAURADAR_CLOSED_TEST_PASSWORD in Render entfernen und deployen, wodurch die beiden reservierten Testkonten samt Daten entfernt werden; GitHub-Testsecret ebenfalls entfernen. Öffentliche Registrierung bleibt false. Cleanup-Live-Nachweis steht noch aus.

## Testbereinigung und Abschluss
Der Betreiber bestätigt am 06.10.2026 die Entfernung von BAURADAR_CLOSED_TEST_PASSWORD in Render mit anschließendem Deployment sowie die Löschung des gleichnamigen GitHub-Secrets.
Öffentliche Live-Prüfung nach Bereinigung erfolgreich: https://github.com/P68554185/opportunity-radar/actions/runs/37438407621 — Anwendung, Datenbank, dynamischer geprüfter Feed, geschlossene Registrierung und anonymer Zugriffsschutz funktionsfähig.
Die Startup-Bereinigung der beiden reservierten Konten wurde in CI nachgewiesen (37433704129). Die tatsächlichen Kontodatensätze auf Neon wurden nach der Betreiberbereinigung nicht separat ausgelesen; keine Behauptung eines direkten Live-Löschungsnachweises.
Geschlossener Live-Kontotest und Live-Profil-/Merkliste-Persistenz bestanden. E-Mail, Bezahlung, Radius und produktive Sicherungsplanung bleiben offen. Keine verkaufsfähige GO-LIVE-Freigabe allein aus diesen Kontotests abgeleitet.
