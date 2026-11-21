#!/usr/bin/env python3
"""serafino-mehr-zeit.py - „Mehr Zeit bitte“ (be15).

Das Kind bittet um 15 Minuten. Fino erklärt, dass Mama oder Papa das
freigeben, dann kommt das Passwort-Fenster („Bitte Mama oder Papa …“).
Mit dem Eltern-Passwort gibt es heute 15 Minuten mehr (Timekpr), ohne
Passwort passiert nichts.

Zu finden: Restzeit-Anzeige in der Taskleiste (antippen), Fino-Hinweise bei
15/5/1 Minute und der Startbildschirm der Kleinen (neben der Sonne).
"""
import datetime
import glob
import os
import pwd
import subprocess
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout

FINO = "/usr/share/serafino/fino/fino.png"
FINO_PARTY = "/usr/share/serafino/fino/fino-party.png"
HELPER = ["pkexec", "/usr/local/bin/serafino-root-helper"]
MINUTEN = 15


def sprich(text):
    for cmd in (["espeak-ng", "-v", "de", "-s", "140", text], ["spd-say", "-l", "de", text]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue


class Fenster(QDialog):
    def __init__(self, bild, gross, klein, knoepfe):
        super().__init__()
        self.setWindowTitle("Fino")
        self.setWindowIcon(QIcon(FINO))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)
        self.wahl = None
        v = QVBoxLayout(self)
        v.setContentsMargins(36, 28, 36, 24)
        v.setSpacing(14)
        b = QLabel()
        pm = QPixmap(bild)
        if not pm.isNull():
            b.setPixmap(pm.scaledToHeight(150, Qt.TransformationMode.SmoothTransformation))
        b.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(b)
        t = QLabel(gross)
        f = QFont(self.font()); f.setPointSizeF(f.pointSizeF() * 1.9); f.setBold(True)
        t.setFont(f); t.setWordWrap(True); t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        v.addWidget(t)
        if klein:
            k = QLabel(klein)
            f2 = QFont(self.font()); f2.setPointSizeF(f2.pointSizeF() * 1.25)
            k.setFont(f2); k.setWordWrap(True); k.setAlignment(Qt.AlignmentFlag.AlignCenter)
            k.setStyleSheet("color:#56636f")
            v.addWidget(k)
        h = QHBoxLayout()
        h.addStretch(1)
        for wert, text, farbe in knoepfe:
            p = QPushButton(text)
            p.setMinimumSize(170, 56)
            p.setFont(QFont(self.font().family(), int(self.font().pointSizeF() * 1.3)))
            p.setStyleSheet("QPushButton{background:%s;color:white;border:none;border-radius:16px;"
                            "padding:8px 22px}" % farbe)
            p.clicked.connect(lambda _=False, w=wert: self.fertig(w))
            h.addWidget(p)
        h.addStretch(1)
        v.addLayout(h)
        self.setMinimumWidth(480)
        QTimer.singleShot(400, lambda: sprich(gross + " " + klein))

    def fertig(self, w):
        self.wahl = w
        self.accept()


def vergessen():
    """Das Eltern-Passwort nicht ein paar Minuten lang merken (polkit „keep“) –
    sonst gäbe es gleich nochmal 15 Minuten ohne Passwort."""
    try:
        subprocess.run(["pkcheck", "--revoke-temp"], capture_output=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        pass


def merker_loeschen():
    """Fino soll bei 15/5/1 Minute wieder Bescheid sagen (Zeit ist ja wieder mehr)."""
    heute = datetime.date.today().isoformat()
    for p in glob.glob(os.path.expanduser("~/.local/state/serafino/fino-zeit-%s" % heute)):
        try:
            os.remove(p)
        except OSError:
            pass


def main():
    user = pwd.getpwuid(os.getuid()).pw_name
    app = QApplication(sys.argv)
    app.setDesktopFileName("serafino-mehr-zeit")
    frage = Fenster(FINO, "Noch %d Minuten?" % MINUTEN,
                    "Das dürfen Mama oder Papa entscheiden. Hol sie her – sie geben es mit "
                    "ihrem Passwort frei.",
                    [("ja", "🙋 Mama oder Papa fragen", "#2e8a57"), ("nein", "Nein, danke", "#8a97a3")])
    frage.exec()
    if frage.wahl != "ja":
        return 0
    r = subprocess.run(HELPER + ["tk-extra", user, str(MINUTEN * 60)], capture_output=True, text=True)
    vergessen()
    if r.returncode == 0:
        merker_loeschen()
        Fenster(FINO_PARTY if os.path.exists(FINO_PARTY) else FINO, "Juhu! %d Minuten mehr!" % MINUTEN,
                "Viel Spaß – und sag Danke! 😊", [("ok", "OK 👍", "#2e8a57")]).exec()
    elif r.returncode in (126, 127):
        Fenster(FINO, "Diesmal nicht.", "Ohne das Passwort von Mama oder Papa gibt es keine "
                "Extra-Zeit. Vielleicht morgen!", [("ok", "OK", "#2e8a57")]).exec()
    else:
        Fenster(FINO, "Hoppla!", "Das hat gerade nicht geklappt. Mama oder Papa können die Zeit "
                "auch im Kontrollzentrum verlängern.", [("ok", "OK", "#2e8a57")]).exec()
    return 0


if __name__ == "__main__":
    sys.exit(main())
