#!/usr/bin/env python3
"""pingulinux-control-tiles.py - Eltern-Kontrollzentrum als Kachel-Ansicht.

neu mit Qt6 (sieht aus wie KDE). Wird von
pingulinux-parental-control.sh gestartet, nachdem das Eltern-Passwort
geprüft wurde. Jede Kachel startet ein Pingulinux-Werkzeug.
"""
import os
import subprocess
import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QGridLayout, QLabel, QToolButton, QScrollArea, QSizePolicy, QPushButton)

LOGO = "/usr/share/pingulinux/icons/pingu.png"
BIN = "/usr/local/bin/"
ADMIN = BIN + "pingulinux-admin-tool.sh"
STATUS = "/var/lib/pingulinux/sicherung-status"

# Hinweis für einbauen.sh: Konten-Übersicht = pingulinux-admin-tool.sh konten
# (Symbol aus dem KDE-Thema, Titel, Untertitel, Befehl)
TILES = [
    ("preferences-system-time", "Bildschirmzeit", "Zeiten der Kinder", [BIN + "pingulinux-bildschirmzeit.py"]),
    ("system-users", "Benutzerkonten", "Kinder anlegen, Passwörter", [BIN + "pingulinux-manage-users.sh"]),
    ("view-list-details", "Konten-Übersicht", "Alter und Zeiten", [ADMIN, "konten"]),
    ("office-chart-bar", "Nutzung", "Wie lange und womit", [BIN + "pingulinux-statistik.py"]),
    ("applications-games", "Startbildschirm der Kleinen", "Kacheln für 2 bis 6 Jahre", [BIN + "pingulinux-kinderstart.py", "--bearbeiten"]),
    ("applications-multimedia", "YouTube Kids", "Selbst starten oder mit Passwort", [BIN + "pingulinux-youtube-kids-schalter.sh"]),
    ("security-high", "Kinderschutz-Filter", "Webseiten filtern", [BIN + "pingulinux-toggle-dns-filter.sh"]),
    ("firewall-config", "Firewall", "Netzwerk schützen", [ADMIN, "firewall"]),
    ("plasmadiscover", "App Store", "Programme holen", [BIN + "pingulinux-store.py"]),
    ("document-save", "Sicherung", "Sichern und wiederherstellen", [ADMIN, "sicherung"]),
    ("system-software-update", "Update-Assistent", "Aktualisieren", [BIN + "pingulinux-upgrade-assistant.sh"]),
    ("edit-clear-all", "Systembereinigung", "Platz schaffen", [BIN + "pingulinux-cleanup.sh"]),
    ("printer", "Drucker und Scanner", "Einrichten", ["kcmshell6", "kcm_printer_manager"]),
    ("hwinfo", "Hardware & Treiber", "Nvidia, WLAN, neuer Kernel", [BIN + "pingulinux-treiber.py"]),
    ("tools-report-bug", "Fehlerdiagnose", "Was ist los?", [BIN + "pingulinux-diagnose.sh"]),
    ("help-contents", "Hilfe", "Anleitungen und Kontakt", [BIN + "pingulinux-help.sh"]),
]


def start(cmd):
    try:
        subprocess.Popen(cmd, start_new_session=True)
    except OSError:
        pass


# Ersatz-Symbole, falls ein Name im KDE-Symbolthema fehlt
ERSATZ = {"firewall-config": "security-high", "plasmadiscover": "system-software-install",
          "hwinfo": "cpu", "applications-games": "preferences-desktop-user",
          "office-chart-bar": "view-statistics", "applications-multimedia": "media-playback-start"}


def kde_icon(name):
    ic = QIcon.fromTheme(name)
    if ic.isNull() and name in ERSATZ:
        ic = QIcon.fromTheme(ERSATZ[name])
    return ic if not ic.isNull() else QIcon.fromTheme("applications-system")


class KlickLogo(QLabel):
    """Easter Egg: 5× schnell auf das Logo tippen → Fino fliegt über den Bildschirm."""
    def __init__(self):
        super().__init__()
        self.klicks = []
        self.setToolTip("Hallo!")

    def mousePressEvent(self, e):
        import time
        jetzt = time.monotonic()
        self.klicks = [t for t in self.klicks if jetzt - t < 3.0] + [jetzt]
        if len(self.klicks) >= 5:
            self.klicks = []
            try:
                subprocess.Popen([BIN + "pingulinux-fino-flug.py"], start_new_session=True)
            except OSError:
                pass
        super().mousePressEvent(e)


class Tile(QToolButton):
    def __init__(self, icon, title, sub, cmd):
        super().__init__()
        self.setIcon(kde_icon(icon))
        self.setIconSize(QSize(56, 56))
        self.setText("%s\n%s" % (title.replace("&", "&&"), sub))   # „&“ sonst als Tastenkürzel gelesen
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setMinimumSize(170, 150)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setAutoRaise(False)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(sub)
        f = self.font(); f.setPointSizeF(f.pointSizeF() * 1.05); self.setFont(f)
        self.clicked.connect(lambda: start(cmd))


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Eltern-Kontrollzentrum")
        self.resize(900, 700)
        if os.path.exists(LOGO):
            self.setWindowIcon(QIcon(LOGO))

        w = QWidget(); self.setCentralWidget(w)
        v = QVBoxLayout(w)
        v.setContentsMargins(22, 18, 22, 16)

        head = QHBoxLayout()
        if os.path.exists(LOGO):
            logo = KlickLogo()
            logo.setPixmap(QIcon(LOGO).pixmap(56, 56))
            head.addWidget(logo)
        t = QLabel("Hallo! Was möchtest du verwalten?")
        f = t.font(); f.setPointSizeF(f.pointSizeF() * 1.5); f.setBold(True); t.setFont(f)
        head.addWidget(t, 1)
        v.addLayout(head)

        # Sicherung auf einen Blick + „Gestern wiederherstellen“
        info = QHBoxLayout()
        try:
            st = open(STATUS).read().strip()
        except OSError:
            st = "noch nicht gelaufen"
        b_ikon = QLabel()
        b_ikon.setPixmap(kde_icon("document-save").pixmap(22, 22))
        info.addWidget(b_ikon)
        self.backup = QLabel("Tägliche Sicherung: " + st)
        self.backup.setWordWrap(True)
        info.addWidget(self.backup, 1)
        undo = QPushButton(QIcon.fromTheme("edit-undo"), "Gestern wiederherstellen …")
        undo.setToolTip("Läuft nach einem Update etwas nicht mehr? Einen älteren Stand zurückholen.")
        undo.clicked.connect(lambda: start([BIN + "pingulinux-wiederherstellen.py"]))
        info.addWidget(undo)
        v.addLayout(info)

        grid_w = QWidget()
        grid = QGridLayout(grid_w)
        grid.setSpacing(14)
        cols = 4
        for i, (icon, title, sub, cmd) in enumerate(TILES):
            grid.addWidget(Tile(icon, title, sub, cmd), i // cols, i % cols)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(grid_w)
        v.addWidget(scroll, 1)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("pingulinux-kontrollzentrum")
    app.setDesktopFileName("pingulinux-parental-control")
    win = Window()
    win.show()
    sys.exit(app.exec())
