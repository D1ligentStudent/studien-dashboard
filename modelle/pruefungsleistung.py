"""Represent one exam result, with an optional date and a derived status."""

from modelle.pruefungsart import Pruefungsart
from modelle.pruefungsstatus import Pruefungsstatus
from modelle.validierung import _datum, _note


class Pruefungsleistung:
    """Hold the current result rather than a history of exam attempts."""

    def __init__(self, art):
        if not isinstance(art, Pruefungsart):
            raise ValueError('Bitte Klausur oder Projekt auswählen.')
        self.art = art
        self.note = 0.0
        self.datum = None
        self.bestanden_ohne_note = False

    @property
    def status(self):
        """Derive the status each time so it cannot disagree with the result."""
        if self.bestanden_ohne_note:
            return Pruefungsstatus.BESTANDEN
        if 1 <= self.note <= 4:
            return Pruefungsstatus.BESTANDEN
        if self.note > 4:
            return Pruefungsstatus.NICHT_BESTANDEN
        return Pruefungsstatus.UNBENOTET

    def pruefen(self, benotet=True):
        """Reject contradictory graded and ungraded result values."""
        if not isinstance(self.art, Pruefungsart):
            raise ValueError('Bitte Klausur oder Projekt auswählen.')
        if type(benotet) is not bool:
            raise ValueError('Benotet muss ja oder nein sein.')
        _note(self.note)
        if self.datum is not None:
            _datum(self.datum, 'Prüfungsdatum')
        if type(self.bestanden_ohne_note) is not bool:
            raise ValueError('Bestanden ohne Note muss ja oder nein sein.')
        if benotet and self.bestanden_ohne_note:
            raise ValueError(
                'Ein benotetes Modul braucht eine Zahlennote. '
                'Bitte das Ergebnis zuerst zurücksetzen.'
            )
        if not benotet and self.note != 0:
            raise ValueError(
                'Ein unbenotetes Modul erhält keine Zahlennote. '
                'Bitte das Ergebnis zuerst zurücksetzen.'
            )
