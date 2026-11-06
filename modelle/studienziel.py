"""Store the completion date, fixed ECTS target, and desired grade average."""

from modelle.validierung import _datum, _note


class Studienziel:
    """Store the completion date, fixed ECTS target, and desired grade average."""

    def __init__(self, abschlussdatum, ziel_ects, zielnote):
        self.abschlussdatum = _datum(abschlussdatum, 'Abschlussdatum')
        if type(ziel_ects) is not int or ziel_ects != 180:
            raise ValueError('Der Studienplan umfasst fest 180 ECTS.')
        self.ziel_ects = 180
        self.zielnote = _note(zielnote, 4.0)
        if self.zielnote == 0:
            raise ValueError('Bitte eine Zielnote von 1 bis 4 eingeben.')
