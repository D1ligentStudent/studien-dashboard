"""Hold module information and exactly one exam result."""

from modelle.modulart import Modulart
from modelle.pruefungsart import Pruefungsart
from modelle.pruefungsleistung import Pruefungsleistung
from modelle.pruefungsstatus import Pruefungsstatus
from modelle.validierung import _positive_ganzzahl, _text


class Modul:
    """Hold module information and exactly one exam result."""

    def __init__(self, code, titel, ects, benotet=True,
                 modulart=Modulart.PFLICHT, pruefungsart=Pruefungsart.KLAUSUR):
        self.code = _text(code, 'Modulcode')
        self.titel = _text(titel, 'Modultitel')
        self.ects = ects
        if type(benotet) is not bool:
            raise ValueError('Benotet muss ja oder nein sein.')
        if not isinstance(modulart, Modulart):
            raise ValueError('Bitte Pflicht oder Wahlpflicht auswählen.')
        self.benotet = benotet
        self.modulart = modulart
        self.semester = None
        self.pruefung = Pruefungsleistung(pruefungsart)

    @property
    def ects(self):
        return self._ects

    @ects.setter
    def ects(self, wert):
        wert = _positive_ganzzahl(wert, 'Modul-ECTS')
        if wert > 180:
            raise ValueError('Ein Modul darf höchstens 180 ECTS haben.')
        self._ects = wert

    @property
    def bestanden(self):
        return self.pruefung.status is Pruefungsstatus.BESTANDEN

    def ergebnis_setzen(self, note, datum=None, bestanden_ohne_note=False):
        """Validate a temporary result before updating the existing exam object."""
        neues_ergebnis = Pruefungsleistung(self.pruefung.art)
        neues_ergebnis.note = note
        neues_ergebnis.datum = datum
        neues_ergebnis.bestanden_ohne_note = bestanden_ohne_note
        neues_ergebnis.pruefen(self.benotet)
        self.pruefung.note = float(note)
        self.pruefung.datum = datum
        self.pruefung.bestanden_ohne_note = bestanden_ohne_note
