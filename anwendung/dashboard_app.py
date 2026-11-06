"""Terminal menus and the actions selected in them."""

import configparser
import sqlite3
from pathlib import Path

from anwendung.dashboard_controller import DashboardController
from anwendung.terminal_view import TerminalView
from repositories.konfig_repository import KonfigRepository
from repositories.sqlite_studium_repository import SQLiteStudiumRepository


class DashboardApp:
    """Start the dashboard and pass menu choices to the controller."""

    def __init__(self, config_pfad, db_pfad):
        self.config_pfad = Path(config_pfad)
        self.db_pfad = Path(db_pfad)

    def start(self):
        """Read the study plan before showing the first menu."""
        view = TerminalView()
        konfig = KonfigRepository()

        try:
            try:
                geladenes_studium = konfig.lade(self.config_pfad)
                studium_repository = SQLiteStudiumRepository(self.db_pfad)
                controller = DashboardController(geladenes_studium, studium_repository)
                controller.lade_studiendaten()
            except (ValueError, OSError, configparser.Error, sqlite3.Error) as fehler:
                raise SystemExit(
                    'Start nicht moeglich: {}. Bitte INI-Datei und Datenbank pruefen.'.format(
                        fehler
                    )
                ) from None

            view.zeige_uebersicht(controller.lade_dashboard_daten())

            while True:
                hauptbereich = view.lies_aktion()
                if hauptbereich == '0':
                    view.zeige_meldung(
                        'Programm beendet. Nicht gespeicherte Studiendaten gehen verloren.'
                    )
                    return

                if hauptbereich == '3':
                    view.zeige_semester(controller.lade_dashboard_daten())
                else:
                    self.untermenue_starten(controller, view, konfig, hauptbereich)

        except (EOFError, KeyboardInterrupt):
            view.zeige_meldung(
                'Eingabe beendet. Nicht gespeicherte Studiendaten gehen verloren.'
            )

    def untermenue_starten(self, controller, view, konfig, hauptbereich):
        """Stay in the selected area until the user chooses to go back."""
        while True:
            anzeigedaten = controller.lade_dashboard_daten()
            if hauptbereich == '1':
                view.zeige_uebersicht(anzeigedaten)
            elif hauptbereich == '2':
                view.zeige_noten(anzeigedaten)
            else:
                view.zeige_module(anzeigedaten)

            auswahl = view.lies_untermenue(hauptbereich)
            if auswahl == '0':
                return

            while True:
                try:
                    self.aktion_ausfuehren(controller, view, konfig, hauptbereich, auswahl)
                    break
                except ValueError as fehler:
                    view.zeige_meldung('Das geht nicht: %s' % str(fehler))
                    # A failed file operation has no new user input to ask for.
                    if hauptbereich == '1' and auswahl in {'2', '3'}:
                        break
                    view.zeige_meldung('Bitte erneut eingeben.')
                except (sqlite3.Error, OSError, configparser.Error) as fehler:
                    view.zeige_meldung(
                        'Laden oder Speichern fehlgeschlagen: %s. '
                        'Bitte die Dateien pruefen und erneut versuchen.' % str(fehler)
                    )
                    break

    def aktion_ausfuehren(self, controller, view, konfig, hauptbereich, aktion):
        """Menu numbers follow the labels printed by TerminalView."""
        # Study settings and file operations.
        if hauptbereich == '1' and aktion == '1':
            neue_grunddaten = view.lies_grunddaten()
            controller.grunddaten_aendern(neue_grunddaten, konfig, self.config_pfad)
            view.zeige_meldung('Grunddaten in der INI gespeichert.')
            return

        if hauptbereich == '1' and aktion == '2':
            controller.speichern()
            view.zeige_meldung('Studiendaten in der Datenbank gespeichert.')
            return

        if hauptbereich == '1' and aktion == '3':
            # Switch plans only after the INI and the database have both loaded.
            geladenes_studium = konfig.lade(self.config_pfad)
            lade_controller = DashboardController(geladenes_studium, controller.repository)
            lade_controller.lade_studiendaten()
            controller.studium = geladenes_studium
            view.zeige_meldung(
                'Datenbankstand geladen. Ungespeicherte Studiendaten wurden verworfen.'
            )
            return

        vorhandene_codes = set()
        for modul in controller.studium.module:
            vorhandene_codes.add(modul.code)

        # Both menu entries use the same result form.
        notenaktion = hauptbereich == '2' and aktion == '1'
        modulaktion = hauptbereich == '4' and aktion == '3'
        if notenaktion or modulaktion:
            self.pruefung_bearbeiten(controller, view, vorhandene_codes)
            return

        if hauptbereich == '2' and aktion == '3':
            view.zeige_offene_pruefungen(controller.lade_dashboard_daten())
            return

        if hauptbereich == '2' and aktion == '2':
            simulierbare_codes = set()
            for modul in controller.studium.module:
                if modul.benotet and not modul.bestanden:
                    simulierbare_codes.add(modul.code)
            if not simulierbare_codes:
                view.zeige_meldung(
                    'Keine offenen benoteten Module fuer eine Simulation vorhanden.'
                )
                return
            simulationsnoten = view.lies_annahmen(simulierbare_codes)
            simulierter_schnitt = controller.simulieren(simulationsnoten)
            view.zeige_meldung(
                'Simulierter Schnitt: %s' % str(round(simulierter_schnitt, 2))
            )
            return

        # Module data are checked before the controller accepts them.
        if hauptbereich == '4' and aktion == '1':
            erfasste_ects = 0
            for modul in controller.studium.module:
                erfasste_ects += modul.ects
            if erfasste_ects >= 180:
                view.zeige_meldung(
                    'Bereits 180 ECTS erfasst. Bitte zuerst ein vorhandenes Modul aendern.'
                )
                return
            neue_moduldaten = view.lies_moduldaten(
                vorhandene_codes, controller.studium.aktuelles_semester
            )
            controller.modul_anlegen(neue_moduldaten)
            view.zeige_meldung(
                'Neues Modul uebernommen. Dauerhaft unter Studium > 2 speichern.'
            )
            return

        if hauptbereich == '4' and aktion == '2':
            if not vorhandene_codes:
                view.zeige_meldung(
                    'Noch kein Modul vorhanden. Bitte zuerst ein Modul erfassen.'
                )
                return
            modulcode = view.lies_modulcode(vorhandene_codes)
            alte_moduldaten = controller.moduldaten(modulcode)
            neue_moduldaten = view.lies_moduldaten(
                vorhandene_codes, alte_moduldaten['semester_nummer'], modulcode
            )

            neues_ergebnis = None
            if neue_moduldaten['benotet'] != alte_moduldaten['benotet']:
                view.zeige_meldung(
                    'Die Benotungsart wurde geaendert. '
                    'Bitte das Pruefungsergebnis neu eingeben.'
                )
                neues_ergebnis = view.lies_pruefungsergebnis(
                    neue_moduldaten['benotet'], alte_moduldaten['datum']
                )
            elif view.lies_ergebnis_aendern():
                neues_ergebnis = view.lies_pruefungsergebnis(
                    neue_moduldaten['benotet'], alte_moduldaten['datum']
                )

            controller.modul_aendern(modulcode, neue_moduldaten, neues_ergebnis)
            view.zeige_meldung(
                'Modul ueberschrieben. Dauerhaft unter Studium > 2 speichern.'
            )
            return

        raise ValueError('Unbekannte Menueaktion.')

    def pruefung_bearbeiten(self, controller, view, codes):
        """Ask for one result and update the selected module."""
        if not codes:
            view.zeige_meldung('Noch kein Modul vorhanden. Bitte zuerst ein Modul erfassen.')
            return
        modulcode = view.lies_modulcode(codes)
        modulwerte = controller.moduldaten(modulcode)
        pruefungswerte = view.lies_pruefungsergebnis(modulwerte['benotet'], modulwerte['datum'])
        controller.pruefung_aendern(
            modulcode,
            pruefungswerte['note'],
            pruefungswerte['datum'],
            pruefungswerte['bestanden_ohne_note'],
        )
        view.zeige_meldung(
            'Pruefungsergebnis ueberschrieben. Dauerhaft unter Studium > 2 speichern.'
        )
