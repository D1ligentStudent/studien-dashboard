"""Store the student name and registration number."""

from modelle.validierung import _text


class Studierendenprofil:
    """Store the student name and registration number."""

    def __init__(self, name, matrikelnummer):
        self.name = _text(name, 'Name')
        self.matrikelnummer = _text(matrikelnummer, 'Matrikelnummer')
