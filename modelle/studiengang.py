"""The study plan, its modules and the values shown in the dashboard."""

from datetime import date
from math import isclose

from modelle.modul import Modul
from modelle.modulart import Modulart
from modelle.pruefungsleistung import Pruefungsleistung
from modelle.semester import Semester
from modelle.studierendenprofil import Studierendenprofil
from modelle.studienziel import Studienziel
from modelle.validierung import _datum, _note, _positive_ganzzahl, _text


class Studiengang:
    """One person's plan, including the fixed six-semester structure."""

    def __init__(self, name, beginn, profil, ziel):
        self.name = _text(name, 'Studiengang')
        self.beginn = _datum(beginn, 'Studienbeginn')
        self.profil = profil
        self.ziel = ziel
        self.aktuelles_semester = 1
        self.semester = []

        for nr in range(1, 7):
            self.semester.append(Semester(nr))

        self.module = []
        self.pruefen()

    def modul_hinzufuegen(self, modul):
        """Validate the new entry before adding it to the plan."""
        if not isinstance(modul, Modul):
            raise ValueError('Bitte ein gueltiges Modul verwenden.')

        erfasste_ects = modul.ects
        for vorhandenes_modul in self.module:
            if vorhandenes_modul.code == modul.code:
                raise ValueError('Diesen Modulcode gibt es schon.')
            if vorhandenes_modul.pruefung is modul.pruefung:
                raise ValueError('Jedes Modul braucht seine eigene Prüfung.')
            erfasste_ects += vorhandenes_modul.ects

        if erfasste_ects > 180:
            raise ValueError('Die Module dürfen zusammen höchstens 180 ECTS haben.')
        if modul.semester not in self.semester:
            raise ValueError('Jedes Modul braucht ein Semester dieses Studienplans.')
        modul.pruefung.pruefen(modul.benotet)
        self.module.append(modul)

    def modul_finden(self, code):
        """Module codes are matched exactly."""
        for modul in self.module:
            if modul.code == code:
                return modul
        raise ValueError('Diesen Modulcode gibt es nicht.')

    def pruefen(self):
        """These checks also apply to objects restored from the database."""
        _text(self.name, 'Studiengang')
        _datum(self.beginn, 'Studienbeginn')
        if not isinstance(self.profil, Studierendenprofil):
            raise ValueError('Bitte ein gueltiges Studierendenprofil verwenden.')
        _text(self.profil.name, 'Name')
        _text(self.profil.matrikelnummer, 'Matrikelnummer')
        if not isinstance(self.ziel, Studienziel):
            raise ValueError('Bitte ein gueltiges Studienziel verwenden.')
        _datum(self.ziel.abschlussdatum, 'Abschlussdatum')
        if type(self.ziel.ziel_ects) is not int or self.ziel.ziel_ects != 180:
            raise ValueError('Der Studienplan umfasst fest 180 ECTS.')
        if self.ziel.abschlussdatum <= self.beginn:
            raise ValueError('Das Abschlussdatum muss nach dem Studienbeginn liegen.')
        gepruefte_zielnote = _note(self.ziel.zielnote, 4.0)
        if gepruefte_zielnote == 0:
            raise ValueError('Bitte eine Zielnote von 1 bis 4 eingeben.')
        if type(self.aktuelles_semester) is not int:
            raise ValueError('Das aktuelle Semester muss zwischen 1 und 6 liegen.')
        if not 1 <= self.aktuelles_semester <= 6:
            raise ValueError('Das aktuelle Semester muss zwischen 1 und 6 liegen.')

        if type(self.semester) is not list or len(self.semester) != 6:
            raise ValueError('Der Studienplan braucht genau sechs Semester.')
        for nr in range(1, 7):
            semester = self.semester[nr - 1]
            if not isinstance(semester, Semester):
                raise ValueError('Bitte gueltige Semester verwenden.')
            if (
                type(semester.nummer) is not int
                or semester.nummer != nr
            ):
                raise ValueError('Die Semester muessen die Nummern 1 bis 6 haben.')
            if (
                type(semester.geplante_ects) is not int
                or semester.geplante_ects != 30
            ):
                raise ValueError('Pro Semester sind genau 30 ECTS vorgesehen.')

        if type(self.module) is not list:
            raise ValueError('Die Module muessen als Liste vorliegen.')
        verwendete_codes = set()
        verwendete_pruefungen = set()
        erfasste_ects = 0
        for modul in self.module:
            if not isinstance(modul, Modul):
                raise ValueError('Bitte gueltige Module verwenden.')

            _text(modul.code, 'Modulcode')
            _text(modul.titel, 'Modultitel')
            _positive_ganzzahl(modul.ects, 'Modul-ECTS')
            if modul.code in verwendete_codes:
                raise ValueError('Ein Modulcode ist doppelt vergeben.')
            verwendete_codes.add(modul.code)
            if modul.semester not in self.semester:
                raise ValueError('Jedes Modul braucht ein Semester dieses Studienplans.')
            if type(modul.benotet) is not bool:
                raise ValueError('Benotet muss ja oder nein sein.')
            if not isinstance(modul.modulart, Modulart):
                raise ValueError('Bitte Pflicht oder Wahlpflicht auswählen.')
            if not isinstance(modul.pruefung, Pruefungsleistung):
                raise ValueError('Jedes Modul braucht eine gueltige Prüfungsleistung.')
            if modul.pruefung in verwendete_pruefungen:
                raise ValueError('Jedes Modul braucht seine eigene Prüfung.')
            verwendete_pruefungen.add(modul.pruefung)
            modul.pruefung.pruefen(modul.benotet)
            erfasste_ects += modul.ects

        if erfasste_ects > 180:
            raise ValueError('Die Module dürfen zusammen höchstens 180 ECTS haben.')

    def _summen(self, module):
        """Only passed modules with a numerical grade contribute to an average."""
        notenpunkte = 0.0
        ects_mit_note = 0
        for modul in module:
            if not modul.bestanden:
                continue
            if not modul.benotet:
                continue
            notenbeitrag = modul.ects * modul.pruefung.note
            notenpunkte += notenbeitrag
            ects_mit_note += modul.ects
        return notenpunkte, ects_mit_note

    def _schnitt(self, module):
        """0.0 is the display's empty value when no grades are available."""
        notenpunkte, ects_mit_note = self._summen(module)
        if ects_mit_note == 0:
            return 0.0
        return notenpunkte / ects_mit_note

    def notensummen(self):
        """Grade total and ECTS weight for all modules in this plan."""
        return self._summen(self.module)

    def notendurchschnitt(self):
        """ECTS-weighted average; ungraded modules do not contribute."""
        return self._schnitt(self.module)

    def erforderlicher_restschnitt(self):
        """Calculate the remaining average and the status of the grade goal.

        Recorded ungraded modules reduce the final grade weight, even if unfinished.
        """
        bisherige_notensumme, abgeschlossene_benotete_ects = self.notensummen()

        erfasste_unbenotete_ects = 0
        for modul in self.module:
            if not modul.benotet:
                erfasste_unbenotete_ects += modul.ects

        # Unrecorded ECTS are assumed to be graded until modules say otherwise.
        abschluss_ects_mit_note = 180 - erfasste_unbenotete_ects
        offene_ects_mit_note = abschluss_ects_mit_note - abgeschlossene_benotete_ects

        if offene_ects_mit_note == 0:
            ziel_erfuellt = False
            zielstatus = 'Kein Notenschnitt berechenbar'
            if abgeschlossene_benotete_ects > 0:
                aktueller_schnitt = self.notendurchschnitt()
                ziel_erfuellt = aktueller_schnitt <= self.ziel.zielnote
                # Treat the decimal target as equal within the calculation tolerance.
                if isclose(
                    aktueller_schnitt, self.ziel.zielnote,
                    rel_tol=0, abs_tol=1e-12,
                ):
                    ziel_erfuellt = True
                zielstatus = 'Ziel nicht erreicht'
                if ziel_erfuellt:
                    zielstatus = 'Ziel erreicht'
            return {
                'rest_ects_benotet': 0,
                'benoetigter_schnitt': 0.0,
                'ziel_erreichbar': ziel_erfuellt,
                'status': zielstatus,
            }

        notensumme_fuer_ziel = self.ziel.zielnote * abschluss_ects_mit_note
        verbleibende_notenpunkte = notensumme_fuer_ziel - bisherige_notensumme
        noetiger_restschnitt = verbleibende_notenpunkte / offene_ects_mit_note

        # Do not turn an exactly achievable 1.0 into an impossible target.
        if isclose(noetiger_restschnitt, 1.0, rel_tol=0, abs_tol=1e-12):
            noetiger_restschnitt = 1.0
        erreichbar = noetiger_restschnitt >= 1
        zielstatus = 'Erreichbar'
        if not erreichbar:
            zielstatus = 'Nicht mehr erreichbar'
        return {
            'rest_ects_benotet': offene_ects_mit_note,
            'benoetigter_schnitt': noetiger_restschnitt,
            'ziel_erreichbar': erreichbar,
            'status': zielstatus,
        }

    def simulieren(self, annahmen):
        """Use proposed passing grades in a calculation, without storing them."""
        simulierte_notensumme, simulierte_ects = self.notensummen()
        for modulcode, vorschlag in annahmen.items():
            modul = self.modul_finden(modulcode)
            gepruefte_note = _note(vorschlag, 4.0)
            if (
                modul.bestanden
                or not modul.benotet
                or gepruefte_note == 0
            ):
                raise ValueError(
                    'Bitte ein offenes benotetes Modul und eine Note von 1 bis 4 auswählen.'
                )
            simulierte_notensumme += modul.ects * gepruefte_note
            simulierte_ects += modul.ects
        if simulierte_ects == 0:
            return 0.0
        return simulierte_notensumme / simulierte_ects

    def erreichte_ects(self):
        """Progress includes every passed module, graded or not."""
        bestandene_ects = 0
        for modul in self.module:
            if modul.bestanden:
                bestandene_ects += modul.ects
        return bestandene_ects

    def fortschritt_prozent(self):
        """The progress target is fixed at 180 ECTS."""
        return 100.0 * self.erreichte_ects() / 180

    def sollfortschritt_ects(self, datum=None):
        """Daily target between the study start and the planned completion date."""
        if datum is None:
            datum = date.today()
        datum = _datum(datum, 'Stichtag')
        geplante_tage = (self.ziel.abschlussdatum - self.beginn).days
        if geplante_tage <= 0:
            raise ValueError('Das Abschlussdatum muss nach dem Studienbeginn liegen.')
        if datum <= self.beginn:
            return 0.0
        if datum >= self.ziel.abschlussdatum:
            return 180.0

        tage_bis_stichtag = (datum - self.beginn).days
        zeitanteil = tage_bis_stichtag / geplante_tage
        return 180.0 * zeitanteil

    def zeitplanabweichung(self, datum=None):
        """Positive means ahead of the daily target, negative means behind."""
        bisher_erreicht = self.erreichte_ects()
        am_stichtag_geplant = self.sollfortschritt_ects(datum)
        return bisher_erreicht - am_stichtag_geplant

    def semestervergleich(self):
        """Collect a separate overview for each of the six semester objects."""
        vergleich = []
        for semester in self.semester:
            semestermodule = []
            bestandene_ects = 0
            for modul in self.module:
                if modul.semester is semester:
                    semestermodule.append(modul)
                    if modul.bestanden:
                        bestandene_ects += modul.ects
            vergleich.append({
                'nummer': semester.nummer,
                'geplante_ects': 30,
                'erreichte_ects': bestandene_ects,
                'schnitt': self._schnitt(semestermodule),
            })
        return vergleich

    def offene_pruefungen(self, datum=None):
        """A missing or failed result stays open, regardless of its exam date."""
        if datum is None:
            datum = date.today()
        datum = _datum(datum, 'Stichtag')
        offen = []
        for modul in self.module:
            if modul.bestanden:
                continue
            pruefungstermin = modul.pruefung.datum
            vergangen = False
            if pruefungstermin is not None:
                vergangen = pruefungstermin < datum
            offen.append({
                'code': modul.code,
                'titel': modul.titel,
                'ects': modul.ects,
                'datum': pruefungstermin,
                'status': modul.pruefung.status.value,
                'termin_vergangen': vergangen,
            })
        return offen
