"""Terminal screens and input forms for the study dashboard.

The controller supplies the values shown here. Input readers repeat a question
until its value is usable; they do not save changes or calculate study results.
"""

from datetime import date

from modelle.modulart import Modulart
from modelle.pruefungsart import Pruefungsart


def _eingabe_text(frage):
    while True:
        text = input(frage + ': ').strip()
        if text:
            return text

        print('Falsch. Bitte einen Text eingeben.')


def _eingabe_auswahl(frage, erlaubte_werte):
    while True:
        antwort = input(frage + ': ').strip().lower()
        if antwort in erlaubte_werte:
            return antwort

        print('Falsch. Bitte eine der angegebenen Moeglichkeiten eingeben.')


def _eingabe_ganzzahl(frage):
    """ECTS must be a whole number within the size of the study plan."""
    while True:
        text = input(frage + ': ').strip()

        try:
            zahl = int(text)
        except ValueError:
            print('Falsch. Bitte eine ganze Zahl von 1 bis 180 eingeben.')
            continue

        if 1 <= zahl <= 180:
            return zahl

        print('Falsch. Bitte eine ganze Zahl von 1 bis 180 eingeben.')


def _eingabe_note(frage):
    """Zero means no result. A comma is accepted as a decimal separator."""
    while True:
        text = input(frage + ': ').strip()

        try:
            note = float(text.replace(',', '.'))
        except ValueError:
            print('Falsch. Bitte 0 oder eine Note von 1 bis 5 eingeben.')
            continue

        if note == 0 or 1 <= note <= 5:
            return note

        print('Falsch. Bitte 0 oder eine Note von 1 bis 5 eingeben.')


def _eingabe_zielnote():
    # A target must be a passing grade, unlike an actual exam result.
    while True:
        note = _eingabe_note('Zielnote (1 bis 4)')
        if 1 <= note <= 4:
            return note

        print('Falsch. Die Zielnote muss zwischen 1 und 4 liegen.')


def _eingabe_datum(frage, leer_erlaubt=True, standard=None):
    """Enter keeps an existing date; '-' clears an optional date."""
    while True:
        text = input(frage + ': ').strip()

        if not text and standard is not None:
            return standard
        if leer_erlaubt and text in {'', '-'}:
            return None

        if len(text) != 10 or text[4] != '-' or text[7] != '-':
            print('Falsch. Bitte ein Datum im Format JJJJ-MM-TT eingeben.')
            continue

        try:
            return date.fromisoformat(text)
        except ValueError:
            print('Falsch. Bitte ein Datum im Format JJJJ-MM-TT eingeben.')


def _eingabe_semester(standard):
    antwort = _eingabe_auswahl(
        'Semester 1 bis 6 (Enter = ' + str(standard) + ')',
        {'', '1', '2', '3', '4', '5', '6'},
    )
    if not antwort:
        return standard
    return int(antwort)


class TerminalView:
    """Show the four dashboard areas and collect their input values."""

    def zeige_uebersicht(self, daten):
        print('Hallo %s | %s' % (daten['name'], daten['studiengang']))

        grunddaten = daten['grunddaten']
        print('Matrikelnummer: %s' % (grunddaten['matrikelnummer'],))
        print('Studienbeginn: %s' % (grunddaten['beginn'].strftime('%d.%m.%Y'),))
        print('Abschlussziel: %s' % (grunddaten['abschlussdatum'].strftime('%d.%m.%Y'),))
        print('Zielnote: %s' % (grunddaten['zielnote'],))

        print('Datum: %s' % (daten['datum'].strftime('%d.%m.%Y'),))
        print('Aktuelles Semester aus INI: %s' % (daten['semester'],))
        print('ECTS: %s / 180' % (daten['erreichte_ects'],))
        print('Fortschritt: %s %%' % (round(daten['fortschritt_prozent'], 2),))
        print('Sollfortschritt bis heute: %s ECTS' % (round(daten['soll_ects'], 2),))
        print('Abweichung vom Zeitplan: %s ECTS' % (round(daten['zeitplanabweichung'], 2),))
        print('Soll am Ende des aktuellen Semesters: %s ECTS' % (daten['semester_soll_ects'],))

        print('Notendurchschnitt: %s' % (round(daten['notendurchschnitt'], 2),))
        rest = daten['restschnitt']
        # A completed grade weight is different from an unreachable target.
        if rest['status'] == 'Nicht mehr erreichbar':
            print('Erforderlicher Restschnitt: Ziel nicht mehr erreichbar')
        elif rest['rest_ects_benotet'] == 0:
            print('Kein weiterer benoteter Restschnitt erforderlich.')
        else:
            print('Erforderlicher Restschnitt: %s' % (round(rest['benoetigter_schnitt'], 2),))
        print(rest['status'])

    def zeige_noten(self, daten):
        print('Noten und Szenarien')
        print('0 = kein Ergebnis | 1 bis 4 = bestanden | ueber 4 bis 5 = nicht bestanden')

        for modul in daten['module']:
            datum = modul['datum']
            if datum is None:
                datum = '-'

            note = modul['note']
            if not modul['benotet']:
                note = 'ohne Zahlennote'

            print(
                '%s %s | Note: %s | %s | Datum: %s'
                % (modul['code'], modul['titel'], note, modul['status'], datum)
            )

        print('Notendurchschnitt: %s' % (round(daten['notendurchschnitt'], 2),))
        print(
            'Offene oder nicht bestandene Pruefungen: %s'
            % (len(daten['offene_pruefungen']),)
        )

    def zeige_offene_pruefungen(self, daten):
        """A past date is a reminder, not an automatically failed exam."""
        print(
            'Offene oder nicht bestandene Pruefungen am %s'
            % (daten['datum'].strftime('%d.%m.%Y'),)
        )
        if not daten['offene_pruefungen']:
            print('Keine offenen Pruefungen vorhanden.')

        for pruefung in daten['offene_pruefungen']:
            datum = pruefung['datum']
            if datum is None:
                datum = 'ohne Termin'

            print(
                '%s %s | %s ECTS | %s | %s'
                % (
                    pruefung['code'],
                    pruefung['titel'],
                    pruefung['ects'],
                    datum,
                    pruefung['status'],
                )
            )
            if pruefung['termin_vergangen']:
                print('  Termin liegt in Vergangenheit.')

    def zeige_semester(self, daten):
        print('Semestervergleich: je Semester sind 30 ECTS vorgesehen.')

        for semester in daten['semestervergleich']:
            print(
                'Semester %s | %s / 30 ECTS | Schnitt: %s'
                % (
                    semester['nummer'],
                    semester['erreichte_ects'],
                    round(semester['schnitt'], 2),
                )
            )

        print(
            'Aktuelles Semester: %s | Soll am Semesterende: %s ECTS'
            % (daten['semester'], daten['semester_soll_ects'])
        )
        print('Die Semesternummer wird ausschliesslich in daten/studium.ini festgelegt.')

    def zeige_module(self, daten):
        print('Module')

        for modul in daten['module']:
            benotung = 'benotet'
            if not modul['benotet']:
                benotung = 'ohne Zahlennote'

            print(
                '%s %s | %s ECTS | Semester: %s | %s | %s'
                % (
                    modul['code'],
                    modul['titel'],
                    modul['ects'],
                    modul['semester_nummer'],
                    modul['modulart'].value,
                    benotung,
                )
            )

    def lies_aktion(self):
        print(
            '\n1 Studium | 2 Noten und Szenarien | 3 Semester | 4 Module | 0 Ende'
        )
        return _eingabe_auswahl('Hauptbereich', {'0', '1', '2', '3', '4'})

    def lies_untermenue(self, hauptbereich):
        if hauptbereich == '1':
            print(
                '1 Grunddaten aendern | 2 Studiendaten speichern '
                '| 3 Studiendaten neu laden | 0 Zurueck'
            )
            erlaubt = {'0', '1', '2', '3'}
        elif hauptbereich == '2':
            print(
                '1 Pruefungsergebnis eintragen oder aendern | 2 Notensimulation '
                '| 3 Offene Pruefungen | 0 Zurueck'
            )
            erlaubt = {'0', '1', '2', '3'}
        else:
            print(
                '1 Neues Modul | 2 Modul bearbeiten '
                '| 3 Pruefungsergebnis bearbeiten | 0 Zurueck'
            )
            erlaubt = {'0', '1', '2', '3'}

        return _eingabe_auswahl('Aktion', erlaubt)

    def lies_modulcode(self, bekannte_codes):
        while True:
            code = _eingabe_text('Welches Modul? Modulcode')
            if code in bekannte_codes:
                return code

            print('Falsch. Bitte einen vorhandenen Modulcode eingeben.')

    def lies_moduldaten(self, bekannte_codes, semester_standard, modulcode=None):
        """Reuse a supplied code when editing; ask for the other fields again."""
        if modulcode is None:
            while True:
                modulcode = _eingabe_text('Neuer Modulcode (z. B. 1)')
                if modulcode not in bekannte_codes:
                    break
                print('Falsch. Diesen Modulcode gibt es schon.')

        titel = _eingabe_text('Modultitel')
        ects = _eingabe_ganzzahl('ECTS')
        semester = _eingabe_semester(semester_standard)

        art = _eingabe_auswahl('1 Pflicht | 2 Wahlpflicht (Enter = Pflicht)', {'', '1', '2'})
        modulart = Modulart.PFLICHT
        if art == '2':
            modulart = Modulart.WAHLPFLICHT

        art = _eingabe_auswahl('1 Klausur | 2 Projekt (Enter = Klausur)', {'', '1', '2'})
        pruefungsart = Pruefungsart.KLAUSUR
        if art == '2':
            pruefungsart = Pruefungsart.PROJEKT

        antwort = _eingabe_auswahl('Mit Zahlennote? j/n (Enter = j)', {'', 'j', 'n'})
        benotet = antwort != 'n'

        return {
            'code': modulcode,
            'titel': titel,
            'ects': ects,
            'semester_nummer': semester,
            'modulart': modulart,
            'pruefungsart': pruefungsart,
            'benotet': benotet,
        }

    def lies_pruefungsergebnis(self, benotet=True, datum_standard=None):
        """Ungraded results use a pass flag instead of a made-up numeric grade."""
        note = 0.0
        bestanden_ohne_note = False

        if benotet:
            note = _eingabe_note('Note (0 = offen oder 1 bis 5)')
        else:
            print('Diese Leistung hat keine Zahlennote.')
            antwort = _eingabe_auswahl('Bestanden? j/n (Enter = n)', {'', 'j', 'n'})
            bestanden_ohne_note = antwort == 'j'

        frage = 'Pruefungsdatum JJJJ-MM-TT (Enter = ohne Datum)'
        if datum_standard is not None:
            frage = (
                'Pruefungsdatum JJJJ-MM-TT (Enter = '
                + datum_standard.isoformat() + '; - = loeschen)'
            )
        datum = _eingabe_datum(frage, standard=datum_standard)

        return {
            'note': note,
            'datum': datum,
            'bestanden_ohne_note': bestanden_ohne_note,
        }

    def lies_ergebnis_aendern(self):
        antwort = _eingabe_auswahl(
            'Pruefungsergebnis ebenfalls neu eingeben? j/n (Enter = n)',
            {'', 'j', 'n'},
        )
        return antwort == 'j'

    def lies_annahmen(self, offene_codes):
        """A blank module code finishes this set of simulation inputs."""
        annahmen = {}

        while True:
            code = input('Modulcode fuer Simulation (Enter beendet): ').strip()
            if not code:
                return annahmen
            if code not in offene_codes:
                print('Falsch. Bitte ein offenes, benotetes Modul waehlen.')
                continue

            while True:
                note = _eingabe_note('Angenommene Note (1 bis 4)')
                if 1 <= note <= 4:
                    annahmen[code] = note
                    break
                print('Falsch. Eine angenommene bestandene Note muss zwischen 1 und 4 liegen.')

    def lies_grunddaten(self):
        """The current semester is edited in the INI, not in this form."""
        name = _eingabe_text('Name')
        matrikelnummer = _eingabe_text('Matrikelnummer')
        studiengang = _eingabe_text('Studiengang')

        beginn = _eingabe_datum('Studienbeginn JJJJ-MM-TT', leer_erlaubt=False)
        while True:
            abschluss = _eingabe_datum('Abschlussdatum JJJJ-MM-TT', leer_erlaubt=False)
            if abschluss > beginn:
                break
            print('Falsch. Das Abschlussdatum muss nach dem Studienbeginn liegen.')

        zielnote = _eingabe_zielnote()

        return {
            'name': name,
            'matrikelnummer': matrikelnummer,
            'studiengang': studiengang,
            'beginn': beginn,
            'abschlussdatum': abschluss,
            'ziel_ects': 180,
            'zielnote': zielnote,
        }

    def zeige_meldung(self, text):
        print(text)
