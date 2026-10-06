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
| Geschlossener Kontotest | Live-Test auf Render/Neon erfolgreich | 37435166258, Versuch 3: zwei Konten, Profile/Merklisten, Logout/Login, Secure-Cookies; Redeploy-Persistenz offen |
| Betriebsprofile / Merkliste / Login | implementiert, SQLite/PostgreSQL und Browser geprüft | Registrierung öffentlich deaktiviert; zwei synthetische Konten live geprüft |
| Prozessneustart / Kontotrennung | CI erfolgreich | Echter Neustart mit PostgreSQL; zwei Konten im Browser; CI 37431562638 |
| Automatischer Render-Feed | auf Render veröffentlicht und live geprüft | Geprüfte Pages-Daten per Servercache übernehmen, ohne täglichen Redeploy |
| PostgreSQL-Sicherung / Restore | Werkzeuge integriert; Wiederherstellung in CI erfolgreich | Produktive Sicherungsplanung und verschlüsselte Ablage offen |
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
1. PR #5 integriert und vollständig geprüft (CI 37431562638): automatische Feed-Übernahme, Prozessneustart und Browser-Kontotrennung.
2. Render-Feed veröffentlicht und live geprüft (37432113469); kein erneutes Deployment allein für die Wartungswerkzeuge erforderlich.
3. Geschlossener Kontotest live bestanden (37435166258, Versuch 3). Jetzt manueller Render-Redeploy und zweiter Workflow mit verify_persistence=true; danach Testsecret entfernen und Cleanup deployen.
4. PostgreSQL-Backup/Restore in CI bestanden (37432784843). Produktive Sicherungsplanung/geschützte Ablage und persistente Konten über echten Render-Redeploy noch prüfen.
5. Radius, weitere EARLY-Quellen, E-Mail sowie Angebot/Rechtstexte vervollständigen.

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
