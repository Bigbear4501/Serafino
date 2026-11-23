"""Serafino: Qt-Fenster auf Deutsch.

Qt übersetzt seine eigenen Texte (Rechtsklick-Menü „Kopieren/Einfügen“,
Standard-Knöpfe „OK/Abbrechen“, Datei-Dialoge, YouTube-Kids-Browser) nur,
wenn ein Programm die Übersetzung ausdrücklich lädt. Das macht dieses Modul.

Benutzung (direkt nach dem Erzeugen der QApplication):
    import serafino_deutsch; serafino_deutsch.an(app)

Die Übersetzungsdateien kommen aus dem Debian-Paket qt6-translations-l10n.
Fehlt etwas, passiert einfach nichts – das Programm läuft normal weiter.
"""

_GELADEN = []


def an(app=None):
    try:
        from PyQt6.QtCore import QCoreApplication, QLibraryInfo, QLocale, QTranslator
    except Exception:
        return 0
    app = app or QCoreApplication.instance()
    if app is None:
        return 0
    ort = QLocale.system()
    if not ort.name().startswith("de"):
        ort = QLocale("de_DE")
    pfade = []
    try:
        pfade.append(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
    except Exception:
        pass
    pfade += ["/usr/share/qt6/translations"]
    anzahl = 0
    for name in ("qtbase", "qtwebengine", "qtmultimedia", "qtdeclarative"):
        for pfad in pfade:
            t = QTranslator(app)
            if t.load(ort, name, "_", pfad):
                app.installTranslator(t)
                _GELADEN.append(t)          # Verweis behalten, sonst räumt Python ihn weg
                anzahl += 1
                break
    return anzahl
