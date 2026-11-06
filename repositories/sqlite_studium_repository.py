"""Store the current module plan and its exam results in SQLite."""

from datetime import date
from pathlib import Path
import sqlite3

from modelle.modul import Modul
from modelle.modulart import Modulart
from modelle.pruefungsart import Pruefungsart
from modelle.studiengang import Studiengang
from repositories.studium_repository import StudiumRepository


class SQLiteStudiumRepository(StudiumRepository):
    """Use the existing twotable format without replacing user data on startup."""

    def __init__(self, pfad):
        self.pfad = Path(pfad)
        self.initialisieren()

    def _verbindung(self):
        """Return a connection whose result columns can be read by name."""
        verbindung = sqlite3.connect(self.pfad)
        verbindung.row_factory = sqlite3.Row
        verbindung.execute('PRAGMA foreign_keys = ON')
        return verbindung

    def initialisieren(self):
        """Create missing tables, without adding modules or sample results."""
        verbindung = self._verbindung()
        try:
            verbindung.executescript('''
                CREATE TABLE IF NOT EXISTS module (
                    code TEXT PRIMARY KEY,
                    titel TEXT NOT NULL,
                    ects INTEGER NOT NULL CHECK (ects BETWEEN 1 AND 180),
                    benotet INTEGER NOT NULL CHECK (benotet IN (0,1)),
                    modulart TEXT NOT NULL,
                    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 6)
                );
                CREATE TABLE IF NOT EXISTS pruefungen (
                    modulcode TEXT PRIMARY KEY REFERENCES module(code) ON DELETE CASCADE,
                    art TEXT NOT NULL,
                    datum TEXT,
                    note REAL NOT NULL CHECK (note = 0 OR note BETWEEN 1 AND 5),
                    bestanden_ohne_note INTEGER NOT NULL CHECK (bestanden_ohne_note IN (0,1))
                );
            ''')
            verbindung.commit()
        finally:
            verbindung.close()

    def speichere_studiendaten(self, studium):
        """Commit the whole plan together; any failed transaction is rolled back."""
        studium.pruefen()
        verbindung = self._verbindung()
        try:
            # This context commits on success and rolls back if a statement fails.
            with verbindung:
                verbindung.execute('DELETE FROM pruefungen')
                verbindung.execute('DELETE FROM module')
                for modul in studium.module:
                    verbindung.execute('''
                        INSERT INTO module (code, titel, ects, benotet, modulart, semester)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        modul.code, modul.titel, modul.ects, int(modul.benotet),
                        modul.modulart.value, modul.semester.nummer,
                    ))

                    pruefung = modul.pruefung
                    datum = None
                    if pruefung.datum is not None:
                        datum = pruefung.datum.isoformat()
                    verbindung.execute('''
                        INSERT INTO pruefungen (modulcode, art, datum, note, bestanden_ohne_note)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        modul.code, pruefung.art.value, datum,
                        pruefung.note, int(pruefung.bestanden_ohne_note),
                    ))
        finally:
            verbindung.close()

    def lade_studiendaten(self, studium):
        """Validate a separate plan before replacing any current in-memory data."""
        geladen = Studiengang(studium.name, studium.beginn, studium.profil, studium.ziel)
        geladen.aktuelles_semester = studium.aktuelles_semester
        verbindung = self._verbindung()
        try:
            # Both queries must inspect the same database snapshot.
            verbindung.execute('BEGIN')
            verwaiste_pruefung = verbindung.execute('''
                SELECT p.modulcode
                FROM pruefungen p LEFT JOIN module m ON m.code = p.modulcode
                WHERE m.code IS NULL
                LIMIT 1
            ''').fetchone()
            if verwaiste_pruefung is not None:
                raise ValueError('Eine gespeicherte Prüfung hat kein zugehöriges Modul.')

            zeilen = verbindung.execute('''
                SELECT m.code, m.titel, m.ects, m.benotet, m.modulart, m.semester,
                       p.art, p.datum, p.note, p.bestanden_ohne_note
                FROM module m LEFT JOIN pruefungen p ON p.modulcode = m.code
                ORDER BY m.code
            ''')
            for zeile in zeilen:
                if zeile['art'] is None:
                    raise ValueError('Zu jedem Modul muss eine Prüfungsleistung vorhanden sein.')

                benotet = zeile['benotet']
                ohne_note = zeile['bestanden_ohne_note']
                if type(benotet) is not int or benotet not in (0, 1):
                    raise ValueError('Eine Benotungsangabe in der Datenbank ist ungültig.')
                if type(ohne_note) is not int or ohne_note not in (0, 1):
                    raise ValueError('Eine Bestehensngabe in der Datenbank ist ungültig.')

                semester = zeile['semester']
                if type(semester) is not int or semester not in range(1, 7):
                    raise ValueError('Ein gespeichertes Semester muss eine ganze Zahl von 1 bis 6 sein.')

                datum = zeile['datum']
                if datum is not None:
                    if type(datum) is not str:
                        raise ValueError('Das Prüfungsdatum in der Datenbank ist ungültig.')
                    try:
                        datum = date.fromisoformat(datum)
                    except ValueError as fehler:
                        raise ValueError('Das Prüfungsdatum in der Datenbank ist ungültig.') from fehler

                modul = Modul(
                    zeile['code'], zeile['titel'], zeile['ects'],
                    bool(benotet), Modulart(zeile['modulart']), Pruefungsart(zeile['art']),
                )
                modul.semester = geladen.semester[semester - 1]
                modul.ergebnis_setzen(zeile['note'], datum, bool(ohne_note))
                geladen.modul_hinzufuegen(modul)
            geladen.pruefen()
        finally:
            verbindung.close()

        studium.semester = geladen.semester
        studium.module = geladen.module
