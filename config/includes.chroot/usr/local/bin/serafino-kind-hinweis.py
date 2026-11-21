#!/usr/bin/env python3
"""Kinderfreundliche Meldung mit Fino statt einer Fehlermeldung.

  serafino-kind-hinweis.py                    „Dafür brauchst du Mama oder Papa.“
  serafino-kind-hinweis.py --app NAME.desktop  gesperrtes Programm (Altersgrenze)
  serafino-kind-hinweis.py --terminal          Terminal (Strg+Alt+T)
  serafino-kind-hinweis.py --installieren      App Store: Eltern müssen das Passwort eingeben
  serafino-kind-hinweis.py --entfernen         App Store: Entfernen, ebenso
  serafino-kind-hinweis.py --text "…" [--klein "…"] [--zu SEK]
                                                 eigener Text, optional Untertext und
                                                 Fenster schließt sich nach SEK Sekunden
  … --mehrzeit                                   zusätzlich Knopf „Mehr Zeit bitte“ (be15)

Liest den Satz auch vor (espeak-ng), damit es Kinder verstehen, die noch nicht lesen.
"""
import configparser
import os
import subprocess
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

FINO = "/usr/share/serafino/fino/fino.png"
APPDIRS = ["/usr/share/applications", "/var/lib/flatpak/exports/share/applications"]


def app_name(fname):
    """Anzeigename eines Programms aus seiner .desktop-Datei (deutsch, wenn vorhanden)."""
    fname = os.path.basename(fname)
    for d in APPDIRS:
        p = os.path.join(d, fname)
        if os.path.exists(p):
            c = configparser.RawConfigParser(strict=False, interpolation=None)
            try:
                c.read(p, encoding="utf-8")
                e = c["Desktop Entry"]
                return e.get("Name[de]") or e.get("Name") or fname
            except Exception:
                pass
    return fname.rsplit(".desktop", 1)[0].split(".")[-1]


def texte(args):
    if "--app" in args and args.index("--app") + 1 < len(args):
        name = app_name(args[args.index("--app") + 1])
        return ("„%s“ ist noch nichts für dich." % name,
                "Dafür brauchst du Mama oder Papa. Wenn du größer bist, geht es von selbst.")
    if "--terminal" in args:
        return ("Das ist nur für Erwachsene.",
                "Das Terminal brauchen nur Mama oder Papa. Such dir doch ein Spiel aus!")
    if "--installieren" in args:
        return ("Frag Mama oder Papa!",
                "Neue Programme dürfen nur Erwachsene holen. Sie müssen gleich ihr Passwort eingeben.")
    if "--entfernen" in args:
        return ("Frag Mama oder Papa!",
                "Programme entfernen dürfen nur Erwachsene. Sie müssen gleich ihr Passwort eingeben.")
    if "--text" in args and args.index("--text") + 1 < len(args):
        klein = args[args.index("--klein") + 1] if "--klein" in args and args.index("--klein") + 1 < len(args) else ""
        return (args[args.index("--text") + 1], klein)
    return ("Dafür brauchst du Mama oder Papa.", "")


def sprich(text):
    for cmd in (["espeak-ng", "-v", "de", "-s", "140", text], ["spd-say", "-l", "de", text]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue


class Hinweis(QDialog):
    def __init__(self, gross, klein, mehrzeit=False):
        super().__init__()
        self.setWindowTitle("Fino")
        if os.path.exists(FINO):
            self.setWindowIcon(QIcon(FINO))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        v = QVBoxLayout(self)
        v.setContentsMargins(36, 28, 36, 24)
        v.setSpacing(14)
        bild = QLabel()
        pm = QPixmap(FINO)
        if not pm.isNull():
            bild.setPixmap(pm.scaledToHeight(150, Qt.TransformationMode.SmoothTransformation))
        bild.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(bild)
        t = QLabel(gross)
        f = QFont(self.font()); f.setPointSizeF(f.pointSizeF() * 1.9); f.setBold(True)
        t.setFont(f)
        t.setWordWrap(True)
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t)
        if klein:
            k = QLabel(klein)
            f2 = QFont(self.font()); f2.setPointSizeF(f2.pointSizeF() * 1.25)
            k.setFont(f2)
            k.setWordWrap(True)
            k.setAlignment(Qt.AlignmentFlag.AlignCenter)
            k.setStyleSheet("color:#56636f")
            v.addWidget(k)
        h = QHBoxLayout()
        h.addStretch(1)
        ok = QPushButton("OK 👍")
        ok.setMinimumSize(160, 52)
        ok.setFont(QFont(self.font().family(), int(self.font().pointSizeF() * 1.3)))
        ok.setStyleSheet("QPushButton{background:#2e8a57;color:white;border:none;border-radius:16px;padding:8px 24px}")
        ok.clicked.connect(self.accept)
        h.addWidget(ok)
        if mehrzeit:
            mz = QPushButton("🙋 Mehr Zeit bitte")
            mz.setMinimumSize(200, 52)
            mz.setFont(QFont(self.font().family(), int(self.font().pointSizeF() * 1.3)))
            mz.setStyleSheet("QPushButton{background:#f2a51f;color:#1d2329;border:none;border-radius:16px;padding:8px 24px}")
            mz.clicked.connect(self.mehr_zeit)
            h.addSpacing(12)
            h.addWidget(mz)
        h.addStretch(1)
        v.addLayout(h)
        self.setMinimumWidth(460)
        QTimer.singleShot(400, lambda: sprich(gross + " " + klein))

    def mehr_zeit(self):
        try:
            subprocess.Popen(["/usr/local/bin/serafino-mehr-zeit.py"], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass
        self.accept()


def main():
    args = sys.argv[1:]
    app = QApplication(sys.argv)
    app.setDesktopFileName("serafino-kind-hinweis")
    gross, klein = texte(args)
    d = Hinweis(gross, klein, mehrzeit="--mehrzeit" in args)
    if "--zu" in args and args.index("--zu") + 1 < len(args):
        try:
            QTimer.singleShot(int(args[args.index("--zu") + 1]) * 1000, d.accept)
        except ValueError:
            pass
    d.exec()
    return 0


if __name__ == "__main__":
    sys.exit(main())
