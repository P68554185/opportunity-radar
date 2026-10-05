# BauRadar Backend – vorbereitet, noch nicht produktiv gehostet

FastAPI + SQLite mit persistentem Volume. Wiederverwendung der geprüften Pages-Dateien und Kundensnapshots.
Die Oberfläche erkennt die API automatisch; auf GitHub Pages bleibt sie eine lokale Vorschau.

## Lokaler Start
```sh
python -m pip install -r backend/requirements.txt
python build_snapshot.py
BAURADAR_SECURE_COOKIES=false BAURADAR_ENABLE_SIGNUP=true uvicorn backend.app:app --host 127.0.0.1 --port 8000
```
Origin ist standardmäßig http://localhost:8000; den Browser unter diesem Hostnamen öffnen.
Dies ist ein lokaler Entwicklungsstart, keine öffentliche Produktionskonfiguration.

## Container und Produktion
Container: `docker build -f backend/Dockerfile -t bauradar .`
Snapshot vor dem Containerbuild aus dem zu deployenden Commit erzeugen.
Port 8000 ausschließlich hinter einem TLS-Reverse-Proxy betreiben.
Persistentes Volume an /var/lib/bauradar mounten, Schreibrechte für UID 10001 setzen.
BAURADAR_ORIGIN auf die exakte HTTPS-Produktdomain setzen.
BAURADAR_SECURE_COOKIES=true beibehalten.
BAURADAR_ENABLE_SIGNUP bleibt standardmäßig false, bis Infrastruktur und rechtliche Texte geklärt sind.
BAURADAR_ADMIN_EMAILS erlaubt gezielt registrierte Administrator-Adressen; niemals aus einer Kundenanfrage übernehmen.
BAURADAR_DB zeigt auf die persistente SQLite-Datei.
Keine Secrets, Accountdaten oder Datenbankdateien in Git aufnehmen.

## Implementiert
Session-Cookies mit HttpOnly/SameSite/Secure, PBKDF2-SHA256 mit 600.000 Iterationen und individuellen Salts, gehashte serverseitige Session-Tokens, Ablauf/Löschung bei Logout.
Origin-Prüfung für schreibende Aufrufe, begrenzte Authentifizierungsversuche, validierte Profile, pro Konto getrennte Merklisten.
Geschütztes Admin-Routing, keine öffentlichen Swagger-Seiten, redigierte Validierungsfehler ohne Passwort-Echo.
Healthcheck /api/health prüft den Datenbankzugriff. Er meldet E-Mail und Billing ausdrücklich als nicht eingerichtet.

## Produktionsabnahme noch offen
Host/Domain, TLS-Konfiguration, Backup und Restore-Test, Monitoring, Datenschutz/Impressum, E-Mail-Verifizierung und Passwort-Reset.
SQLite ist für einen einzelnen MVP-Server vorgesehen. Mehrere Instanzen benötigen PostgreSQL und verteilte Limits/Sessions.
Ohne Proxy-Header-Vertrauen teilen Clients hinter einem Proxy zunächst das Authentifizierungslimit; vertrauenswürdige Proxy-IPs müssen bei der konkreten Bereitstellung konfiguriert werden.
Kundenprofile/Merklisten werden nicht automatisch zwischen lokaler Vorschau und Konto kopiert, damit Profile verschiedener Personen auf gemeinsam genutzten Geräten nicht vermischt werden.
