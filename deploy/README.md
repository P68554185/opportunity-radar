# Bereitstellungsvorlage – nicht ausgeführt
Vorgesehen: ein kleiner Linux-Server in der EU mit Docker Compose, einer eigenen Domain und persistentem Speicher.
Es wurde kein Hosting-/Domain-Account angelegt und kein kostenpflichtiger Dienst bestellt.

## Vor einer öffentlichen Bereitstellung
Host und Domain vom Nutzer auswählen/freigeben. DNS A/AAAA auf den Server richten.
Nur Ports 80/443 öffentlich freigeben; Port 8000 bleibt im internen Compose-Netz.
deploy/.env.example als deploy/.env kopieren und Domain setzen.
Signup bleibt bis zur rechtlichen und operativen Abnahme deaktiviert.

## Reviewbare Startbefehle
```sh
docker compose --env-file deploy/.env -f deploy/compose.yml config
docker compose --env-file deploy/.env -f deploy/compose.yml up -d --build
docker compose --env-file deploy/.env -f deploy/compose.yml ps
```
Caddy stellt TLS-Zertifikate für die konfigurierte Domain automatisch bereit.
Backend-Healthcheck: /api/health. Kontrollieren: HTTPS, Secure/HttpOnly-Cookie, Anmeldung/Abmeldung, Profile auf zwei Geräten, Trennung zweier Kunden und Admin-Zugriffsverweigerung.
Ein Kontoregistrierungs- und Restore-Test ist vor dem Verkaufsstart erforderlich.

## Datenaktualisierung
Der Container erzeugt den vollständigen geprüften Snapshot beim Build.
Neue Git-Snapshots benötigen einen erneuten Build aus dem geprüften Commit; automatisierter Backend-Rollout ist noch nicht eingerichtet.
GitHub Pages bleibt unabhängig als Vorschau erhalten.

## Backups und Wiederherstellung
SQLite-WAL-Dateien nicht während des Schreibens einzeln kopieren.
Für konsistente Backups die SQLite-Backup-API verwenden (backend/backup.py), dann verschlüsselt außerhalb des Servers sichern.
Backup-Dateien enthalten personenbezogene Daten und müssen im privaten Speicher mit begrenztem Zugriff liegen.
Vor Freigabe eine Wiederherstellung in einem getrennten Volume testen.
SQLite ermöglicht eine einzelne MVP-Instanz; für mehrere App-Instanzen ist PostgreSQL vorzusehen.

## Noch erforderlich
Budget/Hostingentscheidung, tatsächliche Domain, Serverzugang, rechtliche Texte, E-Mail-Verifikation/Passwort-Reset und Zahlungsaccount.
Dieser Ordner ist ein umsetzbarer Bereitstellungsvorschlag, kein Nachweis eines laufenden SaaS-Produktionssystems.
