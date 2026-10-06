# Geschlossener Kontotest

## Testumfang und Grenzen
Zwei synthetische Konten, keine realen Kundendaten:
- closed-test-one@example.invalid
- closed-test-two@example.invalid

Öffentliche Registrierung bleibt BAURADAR_ENABLE_SIGNUP=false.
Die Konten werden nur angelegt, wenn der Betreiber ein Testpasswort als BAURADAR_CLOSED_TEST_PASSWORD im Host hinterlegt.
Das Testpasswort muss 32–200 Zeichen lang und zufällig erzeugt sein; einen Passwortmanager verwenden.
Der Betreiberzugang zur Secret-Konfiguration ist hierfür erforderlich. Kein Testpasswort oder DB-Secret in Git oder Chat.

Reservierte Konto-IDs und E-Mail-Adressen werden auf Konflikte geprüft. Existierende fremde Konten werden nicht übernommen.
Testkonten erhalten auch bei versehentlicher Aufnahme in die Admin-Allowlist keinen Admin-Zugriff.
Der unveränderte Testschlüssel bewahrt Profile, Merklisten und Sitzungen über Neustarts.
Eine Änderung des Testpassworts rotiert nur die Testkonto-Passwörter und widerruft deren Sitzungen.
Nach Entfernung der Variablen löscht der nächste App-Start ausschließlich diese beiden reservierten Testkonten einschließlich ihrer Profile/Merklisten/Sitzungen.
Nach Entfernung der Variablen ohne Neustart ist der laufende Dienst noch nicht bereinigt.

## Live-Ausführung auf Render/Neon
1. Render → bauradar-pilot → Environment: BAURADAR_CLOSED_TEST_PASSWORD als neuen geheimen Wert hinzufügen. Zufälliges Passwort im Passwortmanager erzeugen, nicht hier teilen.
2. BAURADAR_ENABLE_SIGNUP bleibt false. Auf Render die neue main-Version deployen, sodass die Fixture-Provisionierung vorhanden ist.
3. GitHub → Repository Settings → Secrets and variables → Actions → New repository secret:
   Name BAURADAR_CLOSED_TEST_PASSWORD, Wert identisch zum Render-Testpasswort.
   Nicht BAURADAR_DATABASE_URL hinterlegen; der Browser-Test benötigt keinen Datenbankzugang.
4. GitHub Actions → Closed Live Account Test → Run workflow, Branch main, verify_persistence zunächst false.
5. Workflow-Ergebnis prüfen. Er testet HTTPS/Secure-Cookies, Login, geschlossenes Signup, Profile, Merkliste, zwei getrennte Konten, Logout/Wiederanmeldung und Admin-Verweigerung.
6. Erneut Render → Manual Deploy → Deploy latest commit, dasselbe Testpasswort beibehalten.
7. Closed Live Account Test erneut mit verify_persistence=true starten.
   Dieser Modus prüft die bestehenden Profile/Merklisten vor Änderungen. Er belegt dauerhafte Daten auf Neon nach echtem Render-Redeploy.
   Bestehende Browser-Sitzungen über einen Live-Redeploy sind damit nicht separat geprüft, weil der neue Workflow eine frische Browser-Sitzung startet.
8. Nach Abschluss das Testpasswort aus Render entfernen und deployen. GitHub-Testsecret entfernen.
   Bei diesem Neustart werden ausschließlich die reservierten synthetischen Konten und ihre Daten entfernt; echte Nutzer bleiben erhalten.

Es gibt keine neuen Provisionierungs-/Admin-Endpunkte und keinen öffentlich erreichbaren Registrierungsschalter.
Der Test arbeitet mit normalem Login/Profile/Watch-API. Wiederholter erster Test setzt nur die Daten dieser zwei synthetischen Konten zurück.
Der Persistenzmodus setzt diese Daten nicht vor seiner Prüfung zurück.
Keine Passwort-, Cookie-, Profil- oder Browser-Trace-Artefakte werden veröffentlicht. Workflow-Logs melden nur Prüfschritte/Ergebnisse.

## CI
checks/closed_accounts.py verwendet ohne --live ausschließlich einen lokalen PostgreSQL-Testdienst.
Live-Zugangsdaten dürfen nicht als TEST_POSTGRES_URL gesetzt werden.
CI prüft den geschlossenen Ablauf, tatsächlichen Prozessneustart mit vorhandenen Sitzungen und die automatische Entfernung der Fixtures nach Deaktivierung.
Der CI-Nachweis ersetzt keine Ausführung gegen Render/Neon.
