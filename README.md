# Studien-Dashboard

Gib die gewünschte Menüzahl ein und bestätige mit `Enter`. Die folgenden Menüwege beginnen immer im Hauptmenü. Mit `0` kommst du aus einem Untermenü dorthin zurück. Im Hauptmenü beendet `0` das Programm.

## 1. Zuerst ein Modul anlegen

Falls noch keine Module vorhanden sind, wähle **4 Module > 1 Neues Modul**. Gib einen eindeutigen Code ein, zum Beispiel `PY1`. Ergänze Titel, ECTS und Semester. Wähle dann Pflicht oder Wahlpflicht, Klausur oder Projekt und ob es eine Zahlennote gibt. Merke dir den Modulcode. Über ihn wählst du das Modul später wieder aus.

## 2. Ein Prüfungsergebnis eintragen

Gehe bei Bedarf mit `0` ins Hauptmenü zurück. Wähle dann **2 Noten und Szenarien > 1 Prüfungsergebnis eintragen oder ändern**. Gib den Modulcode und das Ergebnis ein:

- `0`: noch kein Ergebnis
- 1 bis 4: bestanden
- über 4 bis 5: nicht bestanden

Bei unbenoteten Modulen wird stattdessen gefragt, ob sie bestanden sind. Ein neuer Prüfungstermin kann mit `Enter` leer bleiben. Das Datumsformat lautet `JJJJ-MM-TT`.

## 3. Noten simulieren

Wähle **2 Noten und Szenarien > 2 Notensimulation**. Dafür muss mindestens ein benotetes Modul vorhanden sein, das noch offen oder nicht bestanden ist. Gib dessen Code und eine angenommene Note zwischen 1 und 4 ein. Du kannst weitere Module ergänzen. Drücke bei der nächsten Modulcode-Abfrage nur `Enter`, um den simulierten Schnitt anzeigen zu lassen.

Bereits bestandene benotete Module zählen mit ihren echten Noten mit. Andere offene Module ohne Annahme werden nicht eingerechnet. Die Simulation ändert keine echten Ergebnisse.

## 4. Ein Modul bearbeiten

Wähle **4 Module > 2 Modul bearbeiten** und gib den Modulcode ein. Die Angaben werden neu eingegeben; der Code bleibt gleich. Das Ergebnis kannst du behalten oder ebenfalls ändern. Beim Wechsel der Benotungsart musst du es neu eingeben. Beachte die angezeigten Vorgaben für `Enter`. Unter 4 > 3 kannst du auch nur das Prüfungsergebnis bearbeiten.

## 5. Die übrigen Ansichten nutzen

- 1 Studium: Fortschritt, Notenschnitt, Zeitplanabweichung und Restschnitt.
- 1 > 1: Persönliche Angaben und Studienziele ändern. Diese Änderungen werden sofort in der INI gespeichert.
- 2 > 3: Offene und nicht bestandene Prüfungen mit Termin, falls vorhanden.
- 3 Semester: ECTS und Notenschnitt je Semester, verglichen mit 30 Soll-ECTS. Das aktuelle Semester stellst du in `daten/studium.ini` ein.
- 1 > 3: Gespeicherten Stand neu laden. Bei erfolgreichem Laden werden ungespeicherte Änderungen verworfen.

## 6. Speichern und beenden

Neue Module und Ergebnisse werden nicht automatisch gespeichert. Wähle vor dem Beenden **1 Studium > 2 Studiendaten speichern**. Danach führt `0` zurück ins Hauptmenü. Mit einer weiteren `0` beendest du das Programm.

Beim Ändern eines vorhandenen Prüfungstermins behält `Enter` das Datum bei. Ein Minuszeichen (`-`) löscht den Termin.
