"""Start the terminal dashboard using files next to this script."""

from pathlib import Path

from anwendung.dashboard_app import DashboardApp


def starte_dashboard(config_pfad, db_pfad):
    """Start with explicit file paths, also useful for isolated checks."""
    app = DashboardApp(config_pfad, db_pfad)
    app.start()


def main():
    """Find the data directory independently of the current working directory."""
    projektordner = Path(__file__).resolve().parent
    config_pfad = projektordner / 'daten' / 'studium.ini'
    db_pfad = projektordner / 'daten' / 'studium.sqlite3'
    starte_dashboard(config_pfad, db_pfad)


if __name__ == '__main__':
    main()
