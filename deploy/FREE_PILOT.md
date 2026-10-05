# Kostenlose Kundenvalidierung – noch nicht bereitgestellt
Nutzerentscheidung vom 05.10.2026: kein kostenpflichtiges Hosting vor erfolgreicher Kundenvalidierung.
Die nutzbare GitHub-Pages-Vorschau bleibt bestehen.
Vorbereitete Option: Render Free für das unveränderte FastAPI-/Docker-Backend, Neon Free für dauerhafte PostgreSQL-Kundendaten.
Es werden weder ein kostenpflichtiger Plan noch ein Render-Datenträger oder eine zahlungspflichtige Datenbank angelegt.

## Warum eine getrennte Datenbank?
Render Free verliert lokale Dateien bei Neustarts, Redeployments und Ruhephasen. SQLite auf diesem Host wäre deshalb keine dauerhafte Kundenpersistenz.
Die kostenlose Render-PostgreSQL-Datenbank läuft nach 30 Tagen ab und wird für dieses Pilotprojekt nicht verwendet.
Das Backend unterstützt PostgreSQL über BAURADAR_DATABASE_URL. SQLite bleibt für Entwicklung oder späteren Betrieb mit persistentem Volume erhalten.

## Konkrete Einrichtung, sobald Accounts verfügbar sind
1. Render-Free- und Neon-Free-Accounts im Eigentum des Nutzers verwenden. Keine Zahlungsmethode/kein automatisches Upgrade für den Pilot.
2. Ein Neon-Free-Projekt in einer EU-Region anlegen. TLS-Connection-String mit sslmode=require oder strengeren geprüften TLS-Einstellungen als Secret bereithalten.
3. Render mit dem vorhandenen GitHub-Repository verbinden. Blueprint render.yaml ist auf plan: free festgelegt, Region Frankfurt.
4. BAURADAR_DATABASE_URL ausschließlich in Render als Secret setzen. Nicht in Git, öffentliche Logs oder Chat kopieren.
5. Render stellt eine HTTPS-Subdomain bereit; eine gekaufte Domain ist für den Pilot nicht erforderlich. Das Backend nutzt RENDER_EXTERNAL_URL als exakten Cookie-/Origin-Kontext.
6. Registrierung bleibt zunächst deaktiviert. Nach Infrastruktur-/Datenschutz-Abnahme BAURADAR_ENABLE_SIGNUP bewusst freischalten.
7. Persistenz über einen Redeploy und zwei getrennte Kundenkonten prüfen. EU-Region und jeweilige Auftragsverarbeitungsbedingungen vor Kundendatenerfassung klären.

## Grenzen des kostenlosen Pilots
Render schläft nach Inaktivität ein; der erste Aufruf kann etwa eine Minute dauern. Nutzungslimits können den Dienst pausieren.
Neon Free hat Speicher-/Compute-/Transfergrenzen; aktuelle Grenzwerte vor Einrichtung im Anbieter-Dashboard prüfen.
Keine künstlichen Keep-alive-Aufrufe. Render-Healthcheck /api/live fragt die Datenbank nicht ab.
Kein bezahlter SLA-/Produktionsbetrieb, keine automatische Zahlung, keine erfundenen Verfügbarkeitsversprechen.
Bei erfolgreicher Kundenvalidierung kann das bestehende Backend auf bezahlte Infrastruktur wechseln, ohne die Kundenoberfläche neu zu bauen.
E-Mail-Verifizierung/Passwort-Reset, Versand, Zahlung und vollständige rechtliche Texte stehen weiterhin aus.

## Geprüfte Primärquellen (05.10.2026)
- https://render.com/docs/free
- https://neon.com/blog/neon-free-plan-1-gb-per-project (02.10.2026; aktuelle Erweiterung des Free Plans)

## Blocker
Es fehlen Render-/Neon-Accounts bzw. eine sichere verbundene Zugriffsmöglichkeit. Diese neue externe Account-Einrichtung erfordert Nutzerbeteiligung.
Es wurde kein externer Account angelegt und noch kein kostenloses Backend deployt.
