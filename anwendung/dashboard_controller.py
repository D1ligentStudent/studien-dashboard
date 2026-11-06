"""Translate terminal input into model changes and prepare display data."""

from datetime import date

from modelle.modul import Modul
from modelle.studiengang import Studiengang
from modelle.studienziel import Studienziel
from modelle.studierendenprofil import Studierendenprofil
from modelle.validierung import _datum


def _modul_aus_daten(studium, daten, semester_standard):
    """Create a module and attach an existing semester of this study plan."""
    modul = Modul(
        daten['code'],
        daten['titel'],
        daten['ects'],
        benotet=daten['benotet'],
        modulart=daten['modulart'],
        pruefungsart=daten['pruefungsart'],
    )
    nummer = daten.get('semester_nummer', semester_standard)
    if type(nummer) is not int or not 1 <= nummer <= 6:
        raise ValueError('Bitte ein Semester von 1 bis 6 auswaehlen.')
    modul.semester = studium.semester[nummer - 1]
    return modul


class DashboardController:
    """Keep calculation in the model and storage in the repositories."""

    def __init__(self, studium, repository):
        self.studium = studium
        self.repository = repository

    def lade_studiendaten(self):
        """Load saved modules and results into the current study plan."""
        self.repository.lade_studiendaten(self.studium)

    def lade_dashboard_daten(self, datum=None):
        """Use one reference date for every date dependent display value."""
        if datum is None:
            datum = date.today()
        # Validate the optional date even when the study plan has no modules.
        datum = _datum(datum, 'Stichtag')

        module = []
        for modul in self.studium.module:
            module.append(self.moduldaten(modul.code))
        grunddaten = self.grunddaten()

        return {
            'name': grunddaten['name'],
            'studiengang': grunddaten['studiengang'],
            'grunddaten': grunddaten,
            'semester': self.studium.aktuelles_semester,
            'datum': datum,
            'erreichte_ects': self.studium.erreichte_ects(),
            'ziel_ects': self.studium.ziel.ziel_ects,
            'soll_ects': self.studium.sollfortschritt_ects(datum),
            'semester_soll_ects': self.studium.aktuelles_semester * 30,
            'fortschritt_prozent': self.studium.fortschritt_prozent(),
            'notendurchschnitt': self.studium.notendurchschnitt(),
            'zeitplanabweichung': self.studium.zeitplanabweichung(datum),
            'restschnitt': self.studium.erforderlicher_restschnitt(),
            'semestervergleich': self.studium.semestervergleich(),
            'offene_pruefungen': self.studium.offene_pruefungen(datum),
            'module': module,
        }

    def simulieren(self, annahmen):
        """Calculate a scenario without changing any stored result."""
        return self.studium.simulieren(annahmen)

    def moduldaten(self, modulcode):
        """Provide one modules metadata and result for display or editing."""
        modul = self.studium.modul_finden(modulcode)
        return {
            'code': modul.code,
            'titel': modul.titel,
            'ects': modul.ects,
            'benotet': modul.benotet,
            'semester_nummer': modul.semester.nummer,
            'modulart': modul.modulart,
            'pruefungsart': modul.pruefung.art,
            'note': modul.pruefung.note,
            'datum': modul.pruefung.datum,
            'status': modul.pruefung.status.value,
            'bestanden_ohne_note': modul.pruefung.bestanden_ohne_note,
        }

    def grunddaten(self):
        """Provide profile and goal values, the current semester stays in INI."""
        return {
            'name': self.studium.profil.name,
            'matrikelnummer': self.studium.profil.matrikelnummer,
            'studiengang': self.studium.name,
            'beginn': self.studium.beginn,
            'abschlussdatum': self.studium.ziel.abschlussdatum,
            'ziel_ects': self.studium.ziel.ziel_ects,
            'zielnote': self.studium.ziel.zielnote,
        }

    def modul_anlegen(self, moduldaten):
        """Create a complete module before adding it to the plan."""
        semester_standard = self.studium.aktuelles_semester
        modul = _modul_aus_daten(self.studium, moduldaten, semester_standard)
        self.studium.modul_hinzufuegen(modul)

    def modul_aendern(self, modulcode, moduldaten, ergebnis=None):
        """Replace one module only after metadata and result have passed checks."""
        if moduldaten['code'] != modulcode:
            raise ValueError('Der Modulcode bleibt beim Bearbeiten gleich.')
        bisher = self.studium.modul_finden(modulcode)
        ersatz = _modul_aus_daten(self.studium, moduldaten, bisher.semester.nummer)

        ects_summe = ersatz.ects
        for modul in self.studium.module:
            if modul is not bisher:
                ects_summe += modul.ects
        if ects_summe > self.studium.ziel.ziel_ects:
            raise ValueError('Die erfassten Module duerfen zusammen hoechstens 180 ECTS haben.')

        if ergebnis is None:
            ersatz.ergebnis_setzen(
                bisher.pruefung.note,
                bisher.pruefung.datum,
                bisher.pruefung.bestanden_ohne_note,
            )
        else:
            ersatz.ergebnis_setzen(
                ergebnis['note'], ergebnis['datum'], ergebnis['bestanden_ohne_note']
            )

        position = self.studium.module.index(bisher)
        self.studium.module[position] = ersatz

    def pruefung_aendern(self, modulcode, note, datum, bestanden_ohne_note=False):
        """Use the modules validated result update for both result editors."""
        modul = self.studium.modul_finden(modulcode)
        modul.ergebnis_setzen(note, datum, bestanden_ohne_note)

    def grunddaten_aendern(self, grunddaten, konfig_repository, config_pfad):
        """Save validated basic data before updating the live objects."""
        profil = Studierendenprofil(grunddaten['name'], grunddaten['matrikelnummer'])
        ziel = Studienziel(
            grunddaten['abschlussdatum'], grunddaten['ziel_ects'], grunddaten['zielnote']
        )
        eingabe = Studiengang(grunddaten['studiengang'], grunddaten['beginn'], profil, ziel)
        eingabe.aktuelles_semester = self.studium.aktuelles_semester
        eingabe.pruefen()
        konfig_repository.speichere(config_pfad, eingabe)

        self.studium.profil = profil
        self.studium.ziel = ziel
        self.studium.name = eingabe.name
        self.studium.beginn = eingabe.beginn

    def speichern(self):
        """Persist modules and results only after the explicit save command."""
        self.repository.speichere_studiendaten(self.studium)
