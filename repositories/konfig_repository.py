"""Read profile and study-goal settings from an INI file."""

import configparser
from datetime import date
import os
from pathlib import Path
import tempfile

from modelle.studiengang import Studiengang
from modelle.studienziel import Studienziel
from modelle.studierendenprofil import Studierendenprofil


class KonfigRepository:
    """Keep profile settings separate from module and exam data."""

    def lade(self, pfad):
        """Build a study plan only after every required setting is valid."""
        config = configparser.ConfigParser()
        try:
            with open(pfad, encoding='utf-8') as datei:
                config.read_file(datei)
        except FileNotFoundError:
            raise FileNotFoundError(f'Konfigurationsdatei nicht gefunden: {pfad}') from None
        except UnicodeDecodeError as fehler:
            raise ValueError('Die Konfigurationsdatei muss UTF-8-Text enthalten.') from fehler

        ziel_ects = config.getint('Ziel', 'ziel_ects')
        if ziel_ects != 180:
            raise ValueError('Dieser Studienplan umfasst genau 180 ECTS.')

        semester = config.getint('Studium', 'semester', fallback=1)
        if semester not in range(1, 7):
            raise ValueError('Das aktuelle Semester muss zwischen 1 und 6 liegen.')

        profil = Studierendenprofil(
            config.get('Profil', 'name'),
            config.get('Profil', 'matrikelnummer'),
        )
        beginn = date.fromisoformat(config.get('Studium', 'beginn'))
        abschlussdatum = date.fromisoformat(config.get('Ziel', 'abschlussdatum'))
        zielnote = config.getfloat('Ziel', 'zielnote')
        ziel = Studienziel(abschlussdatum, ziel_ects, zielnote)
        studium = Studiengang(config.get('Studium', 'name'), beginn, profil, ziel)
        studium.aktuelles_semester = semester
        studium.pruefen()
        return studium

    def speichere(self, pfad, studium):
        """Replace the INI atomically so a failed write preserves the old file."""
        studium.pruefen()
        pfad = Path(pfad)
        config = configparser.ConfigParser()

        # Preserve unrelated settings instead of discarding them on each save.
        if pfad.exists():
            try:
                with open(pfad, encoding='utf-8') as datei:
                    config.read_file(datei)
            except UnicodeDecodeError as fehler:
                raise ValueError('Die Konfigurationsdatei muss UTF-8-Text enthalten.') from fehler

        for abschnitt in ('Profil', 'Studium', 'Ziel'):
            if not config.has_section(abschnitt):
                config.add_section(abschnitt)

        # Keep legacy INI substitutions, while storing new percent signs literally.
        config.set('Profil', 'name', studium.profil.name.replace('%', '%%'))
        config.set('Profil', 'matrikelnummer', studium.profil.matrikelnummer.replace('%', '%%'))
        config.set('Studium', 'name', studium.name.replace('%', '%%'))
        config.set('Studium', 'beginn', studium.beginn.isoformat())
        config.set('Studium', 'semester', str(studium.aktuelles_semester))
        config.set('Ziel', 'abschlussdatum', studium.ziel.abschlussdatum.isoformat())
        config.set('Ziel', 'ziel_ects', str(studium.ziel.ziel_ects))
        config.set('Ziel', 'zielnote', str(studium.ziel.zielnote))

        temporaerer_pfad = None
        try:
            # The temporary file must be closed before replacement on Windows.
            with tempfile.NamedTemporaryFile(
                mode='w', encoding='utf-8', dir=pfad.parent,
                prefix=pfad.name + '.', suffix='.tmp', delete=False,
            ) as datei:
                temporaerer_pfad = Path(datei.name)
                config.write(datei)
            os.replace(temporaerer_pfad, pfad)
        finally:
            if temporaerer_pfad is not None and temporaerer_pfad.exists():
                temporaerer_pfad.unlink()
