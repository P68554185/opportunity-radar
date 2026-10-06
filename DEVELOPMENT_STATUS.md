# BauRadar – Entwicklungsstatus

Stand: 06.10.2026, Datenlauf 09:56 UTC. Qualität und Funktionsnachweise haben Vorrang vor Terminen.

## Aktueller Entwicklungsblock: Dresden / kommunale Frühquellen / Umkreis

PR #8 ist integriert. Offizielle Quellen werden reproduzierbar aktualisiert; neue Fundstellen
ohne belegtes Datum oder unterstützte Struktur bleiben in der internen Prüfung.
Projektidentität wird konservativ anhand unabhängiger Belege geprüft. Widersprüche bei Ort,
Gebäudeteil, Adresse und Projektart unterdrücken Verbindungen.
Bestätigte Ausschreibungen erscheinen als ein Projekt mit Quellenhistorie und konkreter nächster Handlung.
PR #9 ergänzt die dauerhaft erhaltene Historie und Merkliste-Verweise bei einem wechselnden TED-Fenster.
Auch diese Korrektur ist integriert, neu aufgenommen und nach Veröffentlichung im Browser geprüft.

## Dresdner Pilot – integriert, Veröffentlichung läuft

[PR #10](https://github.com/P68554185/opportunity-radar/pull/10) ist integriert.
Vier datierte kommunale Bekanntmachungen erschließen Wohnbebauung Am Lehmberg/Wirtschaftsweg,
Quartier Ostra-Allee, Königsbrücker Straße Nord und das Wohnquartier Kötzschenbroder/Pieschener Straße.
Sie werden als Bauleitplanung angezeigt, nicht als zugesagte Bauausführung oder bevorstehende Ausschreibung.
Die Stadtplanungsbehörde wird als Verfahrensstelle ausgewiesen, nicht als vermeintlicher Bauherr.

Amtliche Referenzen: 377 Bebauungsplangebiete, 157 Vorhaben-/Erschließungsplangebiete und
67.590 aktive, als Dresden ausgewiesene Adresspunkte. Diese Referenzobjekte sind keine zusätzlichen Opportunities.
Die WFS-Antwort meldet keine überprüfbare Gesamtzahl; eine vollständige kommunale Abdeckung wird deshalb nicht behauptet.
Lizenz: Datenlizenz Deutschland – Namensnennung 2.0; Landeshauptstadt Dresden / Quelle: Geodaten Sachsen.

Der Nutzer wählt seine konkrete Dresdner Betriebsadresse lokal aus. Der Umkreis zeigt nur Projekte,
deren belegtes Plangebiet vollständig innerhalb des Radius liegt. Unbekannte Orte und
Gebiete am Radiusrand werden ausgeschlossen; die Ortssuche bleibt die breitere Alternative.
Entfernung ist ausdrücklich ungefähre Luftlinie zu einem Plangebiet, keine Fahrstrecke oder genaue Baustellenadresse.
Besucher-/Auftraggeberadressen werden nicht als Bauort übernommen.

Aktueller geprüfter Pilot-Snapshot: 60 EARLY-Signale / 60 Masterprojekte, davon vier Dresdner
kommunale Frühprojekte mit belegtem Standort; 705 Kundenkarten auf dem TED-Snapshot 09:56 UTC.
Die laufende Neuaufnahme kann TED-/Feedzahlen verändern.
63 Kern- und 28 Backendtests sowie die realen Browser-/Mobil-, Kontotrennungs-,
PostgreSQL-Neustart/Restore- und Dockerprüfungen sind erfolgreich:
[Push-CI](https://github.com/P68554185/opportunity-radar/actions/runs/37448961789),
[PR-CI](https://github.com/P68554185/opportunity-radar/actions/runs/37449024652).

Pages-Veröffentlichung und neuer Hauptbranch-Datenlauf werden gerade geprüft.
Render benötigt den üblichen manuellen Betreiber-Deploy; die Aufforderung wurde gestellt.
Danach folgt die erste kontrollierte Verfünffachung auf 10.000 aktuelle TED-Meldungen.
Qualifizierung, unsichere Lifecycle-Fälle und unbekannte Standorte bleiben unverändert konservativ.

## Vorheriger verifizierter Datenstand – EARLY-/Lifecycle-Abschluss

| Kennzahl | Geprüfte Baseline | Aktuell |
|---|---:|---:|
| Aktuelle TED-Meldungen | 2.000 | 2.000 |
| Klassifizierte Chancen | 1.926 | 1.928 |
| Qualifizierte TED-Meldungen | 654 | 647 |
| Aktive EARLY-Signale | 37 | 56 |
| Aktive EARLY-Masterprojekte | 36 | 56 |
| Kundenkarten insgesamt | 690 | 701 |
| Bestätigte Links zu aktuellen TED-Meldungen | 0 | 3 |
| Unabhängige bestätigte Projektfälle | 0 | 1 |

19 zusätzliche belegte Frühprojekte: 13 Klinik-/Pflegeschulmaßnahmen und 6 Hamburger Schulbauvorhaben.
Die Masterzahl berücksichtigt außerdem die Trennung einer zuvor unsicher zusammengeführten Hort-/Krippenmaßnahme.
647 qualifizierte TED-Meldungen bilden 645 aktuelle Projektkarten; drei belegte Meldungen desselben Projekts sind zusammengefasst.
Hinzu kommen 56 frühe Projekte. Die TED-Zahlen ändern sich mit dem rollierenden Datenfenster.
Acht registrierte Quelldokumente wurden erfolgreich aktualisiert. Acht Prüfqueue-Einträge sind interne Beobachtungen,
keine zusätzlichen Kundenprojekte. Abdeckung bleibt regional und auf unterstützte Quellen begrenzt.

## Historische Validierung und Grenzen

Alsfeld: offizielle Projektmeldung vom 27.07.2023, zwei eingefrorene reale TED-Meldungen vom
25.09.2026 und 28.09.2026. Zeitabstand: 1.156 bzw. 1.159 Tage.
Dies ist eine jetzt recherchierte Rückschau, kein von BauRadar damals erzielter Vorsprung
und kein Beleg dafür, dass dies die erste Ausschreibung des Projekts war.
Der aktuelle Feed enthält drei bestätigte Alsfeld-Vergabemeldungen (25.09., 28.09. und 05.10.2026; 1.156–1.166 Tage Abstand). Bei einem späteren Ausscheiden bleiben qualifizierte Fakten nur in der Historie.
Zwei weitere Untersuchungsfälle liefern keinen zusätzlichen bestätigten Projektfall:
Warburg bleibt wegen unterschiedlicher Auftraggeberrollen unsicher; bei TH Köln fehlt ein belastbares Veröffentlichungsdatum.

Zwei bekannte positive Paare und acht reale Negativkontrollen werden reproduzierbar geprüft.
Diese gezielt gewählte kleine Stichprobe erlaubt keine Accuracy, Präzision, Recall oder allgemeine Trefferquote.
Ein prospektiver, seit tatsächlicher Erfassung gemessener Ausschreibungsvorsprung ist noch nicht nachgewiesen.
Das Beobachtungsjournal beginnt am tatsächlichen Erfassungstag und wird nicht auf Quelldaten zurückdatiert.
Classification Rate ist keine Accuracy; kommerzieller Score und Belegstärke bleiben getrennt.

## Meilensteine und Planung

Prozentwerte sind begründete Planungsschätzungen, keine Messung von Datenqualität oder Produktionsreife.

| Bereich | Planung | Erreichter Nachweis / Restarbeit |
|---|---:|---|
| Grundarchitektur / Datenmodell | 100 % | Bestehende Architektur weiterverwendet, Historie und Quellenjournal ergänzt |
| Live-Ingestion | 100 % | 2.000 TED, täglicher Lauf; Quellenrefresh mit sicherem Rückfall |
| Klassifizierung / Datenqualität | 90 % | Evidenzgate und Regressionen; unabhängige Bewertungsmenge fehlt |
| EARLY-Signale | 68 % | 60 Signale, zusätzliche kommunale Planungsquellen; regionale Breite fehlt |
| Lifecycle-Verknüpfung | 60 % | Erklärbare Engine, echter rückblickender Projektfall; breitere Validierung fehlt |
| Kundenfeed | 90 % | Geprüfte Karten, belegte Lose zusammengeführt; weitere regionale Relevanzarbeit |
| Account / Pilotbetrieb | 65 % | Render/Neon, geschlossene Konten und Redeploy-Persistenz geprüft; produktive Backups offen |
| Handwerker-UX | 76 % | Einfache mobile Karten, Phase, Handlung und aufklappbare Historie; Kundenfeedback fehlt |

Gesamt Richtung Pilot: **ca. 82 % Planungsschätzung** (vorher ca. 80 %).
Der Fortschritt beruht auf reproduzierbaren kommunalen Quellen und abgenommenen Standort-/Radiusabläufen; breites Kundenfeedback und Produktionsbetrieb fehlen.
Kein verkaufsfähiger Produktionsbetrieb zugesichert.

## Abnahmen

- [PR #8](https://github.com/P68554185/opportunity-radar/pull/8): integriert.
- [Vollständige PR-CI](https://github.com/P68554185/opportunity-radar/actions/runs/37444529459): erfolgreich; 57 Kern- und 26 Backendtests, Quellen, Datenneubau, PostgreSQL-Neustart/Restore, Kontotrennung, Chromium/Mobil, Docker.
- [Main-CI nach PR #9](https://github.com/P68554185/opportunity-radar/actions/runs/37446261023): erfolgreich.
- [Live-Ingestion](https://github.com/P68554185/opportunity-radar/actions/runs/37446261113): erfolgreich.
- [Pages nach neuem Datenlauf](https://github.com/P68554185/opportunity-radar/actions/runs/37446410618): veröffentlicht.
- [Veröffentlichter Browser-/Mobiltest](https://github.com/P68554185/opportunity-radar/actions/runs/37446453409): erfolgreich.
- [Render-Live-Prüfung, jüngster Versuch am 06.10.2026 09:51 UTC](https://github.com/P68554185/opportunity-radar/actions/runs/37438407621): Backend/Datenbank ok, 700 Karten, Datenstand identisch zu Pages, anonymer Kontozugriff blockiert.
- [Historien-Randfall PR #9](https://github.com/P68554185/opportunity-radar/pull/9): integriert; [CI](https://github.com/P68554185/opportunity-radar/actions/runs/37445900465) erfolgreich mit 59 Kern- und 26 Backendtests, Merkliste-/Mobilregression sowie vollständigen PostgreSQL-/Browser-/Dockerprüfungen.
- Render wurde vom Betreiber deployt und live mit 700 Karten / Datenlauf 09:44 UTC abgenommen. Der spätere Pages-Datenlauf 09:56 UTC enthält 701 Karten und wird vom Servercache im regulären Abstand von bis zu 15 Minuten übernommen; diese letzte Cache-Aktualisierung wurde noch nicht separat live abgenommen.

## Blocker und nächste Schritte

1. Dresden-Veröffentlichung und Render-Deploy abnehmen; anschließend kontrollierte Datenvergrößerung.
2. Weitere kommunale Fundstellen prüfen, zusätzliche Projekte verorten und Nutzen mit echten Dresdner Betrieben testen. Ein neuer bestätigter Dresdner Lifecycle-Fall ist noch nicht nachgewiesen.
3. Produktive Backup-Zeitplanung und verschlüsselte Ablage einrichten; technische Wiederherstellung in CI bereits geprüft.
4. Öffentliches Signup, E-Mail, Passwort-Reset und Bezahlung folgen auf Betreiberwunsch erst nach funktionierender Produktvalidierung.
   Rechtstexte und Angebot/Preis benötigen Betreiberentscheidungen.

## Betrieb und feste Entscheidungen

[Vorschau](https://p68554185.github.io/opportunity-radar/) · [Render-Pilot](https://bauradar-pilot.onrender.com/)

Render Free / Neon Free; kein bezahltes Upgrade ohne Betreiberentscheidung.
Kostenpflichtiges Hosting erst nach erfolgreicher Kundenvalidierung. Ruhephasen und Nutzungslimits bleiben.
Öffentliche Registrierung, E-Mail und Bezahlung sind deaktiviert.
Geschlossene Live-Kontotests und Persistenz nach Render-Redeploy bestanden; Testzugang wurde vom Betreiber bereinigt.
Zugangsdaten und Kundendaten gehören nicht in Repository, öffentliche Logs oder Artefakte.

Details: [EARLY-/Lifecycle-Ledger](docs-internal/EARLY_LIFECYCLE.md),
[Kostenloser Pilot](deploy/FREE_PILOT.md), [Recovery](deploy/POSTGRES_RECOVERY.md).
Frühere Entwicklungsnotizen: [Archiv](docs-internal/DEVELOPMENT_HISTORY_2026-10-06.md).
