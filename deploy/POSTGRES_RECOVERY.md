# PostgreSQL-Sicherung und Wiederherstellung

## Stand und Grenzen
Das Konto-Backend verwendet im kostenlosen Pilot Neon PostgreSQL.
Das Werkzeug ist für eine vertrauenswürdige Wartungsumgebung mit Python/Backend-Abhängigkeiten und PostgreSQL-Clientprogrammen vorgesehen.
pg_dump muss mindestens dieselbe Hauptversion wie der Datenbankserver besitzen. pg_restore muss das verwendete Archivformat unterstützen.
Der Render-App-Container enthält diese Clientprogramme derzeit nicht. Auf Render Free ist kein Wartungs-Shell-Zugriff vorausgesetzt.

Die CI prüft ausschließlich Wegwerf-Datenbanken mit künstlichen Kontodaten.
Das ist kein Nachweis einer laufenden produktiven Sicherung, kein geplanter Sicherungsdienst und kein Restore der echten Kundendaten.

## Private Sicherung
BAURADAR_DATABASE_URL ausschließlich in der geschützten Wartungsumgebung setzen, bei Neon mit TLS sslmode=require oder strenger.
Keine Zugangsdaten als Befehlsargument, in Git oder in öffentliche CI-Konfiguration aufnehmen.

```sh
python -m backend.postgres_backup backup /private/bauradar/accounts-2026-10-06.dump
```

Das Archiv wird neu mit Rechten 0600 angelegt. Existierende Dateien werden nicht überschrieben.
Der Zielpfad muss außerhalb des öffentlichen Repositorys liegen.
pg_dump erzeugt einen konsistenten Datenbank-Snapshot. Bei einem Fehlschlag wird das unvollständige neu angelegte Archiv gelöscht.
Passwörter werden nur dem Client-Prozess über dessen Umgebung übergeben; Client-Fehler werden nicht unredigiert ausgegeben.
Archive enthalten sensible Profile und Zugangshashes: nur in zugriffsgeschützter, verschlüsselter Ablage sichern.
Rechte 0600 ersetzen keine Verschlüsselung. Keine Archive in GitHub-Artefakte oder Pages hochladen.

## Wiederherstellungsprobe
Eine getrennte leere Zieldatenbank bereitstellen. Quelle und Ziel dürfen nicht dieselbe Datenbank sein.
BAURADAR_RESTORE_DATABASE_URL als eigenes Secret setzen; BAURADAR_DATABASE_URL bleibt die Quellenidentität.
Das Archiv muss ein vertrauenswürdiges privates pg_dump-Custom-Archiv sein.

```sh
python -m backend.postgres_backup restore /private/bauradar/accounts-2026-10-06.dump
```

Das Werkzeug prüft Quelle/Ziel und lehnt vorhandene Tabellen, Views, Sequenzen oder benutzerdefinierte Routinen im Ziel ab.
Es verwendet keine DROP-/CLEAN-Optionen. Restore läuft in einer Transaktion; SQL-Fehler führen zum Rollback.
Während der Probe darf niemand parallel das Ziel initialisieren.
Nach der Probe Konto-/Profil-/Merkliste-Daten prüfen. Übernommene Sitzungstokens sind sensible Daten.
Vor einer späteren echten Umschaltung auf eine Wiederherstellung Sitzungstokens invalidieren und erneute Anmeldung verlangen.
Die Produktionsdatenbank wird bei einer Probe nicht überschrieben; eine echte Umschaltung ist eine separate Betriebsentscheidung.

## Vor zahlenden Kunden noch erforderlich
- Regelmäßige produktive Sicherungen und Fehlerbenachrichtigung einrichten.
- Geschützte, verschlüsselte Ablage, Aufbewahrung/Löschung und Zugriffsverantwortung festlegen.
- Den Restore des echten Schemas in einer isolierten Umgebung wiederholen und Wiederherstellungsdauer messen.
- Sicherungsalter und akzeptierbaren Datenverlust mit dem Pilot-Angebot abstimmen.
Kein bezahlter Speicher oder externer Sicherungsaccount wurde angelegt.
