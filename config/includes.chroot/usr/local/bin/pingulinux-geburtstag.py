#!/usr/bin/env python3
"""Easter Egg: Geburtstag. Bei der ersten Anmeldung am Geburtstag (oder in
den Tagen danach, falls das Kind am Tag selbst nicht am Computer war)
begrüßt Fino mit Partyhut das Kind: „Jetzt bist du 7! 🎉“ – mit Konfetti
und vorgelesen. Ältere Konten ohne Tag (nur JJJJ-MM): erste Anmeldung im
Geburtsmonat.

Läuft beim Anmelden (Autostart, --auto). Nur für Kinderkonten mit
Geburtsdatum (/var/lib/pingulinux/birth/NAME). Einmal pro Jahr: Merker in
~/.local/state/pingulinux/geburtstag-JAHR.

Testen (Eltern): pingulinux-geburtstag.py --test [ALTER]
"""
import datetime
import os
import pwd
import random
import subprocess
import sys

from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout

BILD = "/usr/share/pingulinux/fino/fino-party.png"
BIRTHDIR = "/var/lib/pingulinux/birth"
FARBEN = ["#ff5d8f", "#ffd23f", "#4cc9f0", "#7bd389", "#ff9f1c", "#b388ff"]


def ich():
    return pwd.getpwuid(os.getuid()).pw_name


def vorname(user):
    try:
        g = pwd.getpwnam(user).pw_gecos.split(",")[0].strip()
        return (g or user).split()[0]
    except KeyError:
        return user


NACHHOLEN = 14   # so viele Tage nach dem Geburtstag wird der Gruß noch nachgeholt


def geburt(user):
    """(Jahr, Monat, Tag oder None) aus /var/lib/pingulinux/birth/NAME, sonst None."""
    try:
        teile = [int(x) for x in open(os.path.join(BIRTHDIR, user)).read().strip().split("-")]
    except (OSError, ValueError):
        return None
    if len(teile) == 2:
        return teile[0], teile[1], None
    if len(teile) == 3:
        return teile[0], teile[1], teile[2]
    return None


def ist_dran(g, heute):
    """Jahr des Geburtstags, der gerade dran ist (heute oder vor höchstens
    NACHHOLEN Tagen, auch über den Jahreswechsel), sonst None."""
    _, monat, tag = g
    if tag is None:
        return heute.year if monat == heute.month else None
    for jahr in (heute.year, heute.year - 1):
        try:
            fest = datetime.date(jahr, monat, tag)
        except ValueError:                 # 29. Februar in einem normalen Jahr
            fest = datetime.date(jahr, 3, 1)
        if 0 <= (heute - fest).days <= NACHHOLEN:
            return jahr
    return None


def merker(jahr):
    d = os.path.join(os.path.expanduser("~"), ".local", "state", "pingulinux")
    return os.path.join(d, "geburtstag-%d" % jahr)


def sprich(text):
    for cmd in (["espeak-ng", "-v", "de", "-s", "140", text], ["spd-say", "-l", "de", text]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue


class Feier(QWidget):
    def __init__(self, name, alter):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("Alles Gute zum Geburtstag!")
        self.konfetti = []
        lay = QVBoxLayout(self)
        lay.setContentsMargins(40, 40, 40, 40)
        lay.addStretch(1)
        bild = QLabel()
        pm = QPixmap(BILD)
        if not pm.isNull():
            bild.setPixmap(pm.scaledToHeight(min(420, int(QApplication.primaryScreen().size().height() * 0.45)),
                                             Qt.TransformationMode.SmoothTransformation))
        bild.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bild.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay.addWidget(bild)
        gross = QLabel("Hallo %s!\nJetzt bist du %d! 🎉" % (name, alter) if alter
                       else "Hallo %s!\nAlles Gute zum Geburtstag! 🎉" % name)
        f = QFont(self.font()); f.setPointSizeF(f.pointSizeF() * 3.2); f.setBold(True)
        gross.setFont(f)
        gross.setAlignment(Qt.AlignmentFlag.AlignCenter)
        gross.setStyleSheet("color:#1a4f7a; background:transparent")
        lay.addWidget(gross)
        klein = QLabel("Fino wünscht dir alles Gute zum Geburtstag!")
        f2 = QFont(self.font()); f2.setPointSizeF(f2.pointSizeF() * 1.6)
        klein.setFont(f2)
        klein.setAlignment(Qt.AlignmentFlag.AlignCenter)
        klein.setStyleSheet("color:#56636f; background:transparent")
        lay.addWidget(klein)
        lay.addSpacing(24)
        knopf = QPushButton("Danke, Fino! 🎈")
        knopf.setFont(f2)
        knopf.setMinimumHeight(70)
        knopf.setMaximumWidth(420)
        knopf.setStyleSheet("QPushButton{background:#2e8a57;color:white;border:none;border-radius:20px;padding:10px 30px}"
                            "QPushButton:pressed{background:#24724a}")
        knopf.clicked.connect(self.close)
        lay.addWidget(knopf, 0, Qt.AlignmentFlag.AlignCenter)
        lay.addStretch(1)
        self.setStyleSheet("Feier{background:#f3f8fb}")
        t = QTimer(self)
        t.timeout.connect(self.tick)
        t.start(30)
        QTimer.singleShot(60000, self.close)      # nach einer Minute von selbst zu

    def neues_teil(self, oben=True):
        w, h = max(1, self.width()), max(1, self.height())
        return [random.uniform(0, w), random.uniform(-h, 0) if oben else random.uniform(0, h),
                random.uniform(1.5, 4.0), random.uniform(-1, 1), random.uniform(0, 360),
                random.choice(FARBEN), random.uniform(8, 16)]

    def tick(self):
        if not self.konfetti and self.width() > 10:
            self.konfetti = [self.neues_teil(oben=False) for _ in range(140)]
        for k in self.konfetti:
            k[1] += k[2]; k[0] += k[3]; k[4] += 4
            if k[1] > self.height() + 20:
                k[:] = self.neues_teil()
        self.update()

    def paintEvent(self, e):
        p = QPainter(self)
        p.fillRect(self.rect(), QColor("#f3f8fb"))
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(Qt.PenStyle.NoPen)
        for x, y, _, _, rot, farbe, g in self.konfetti:
            p.save(); p.translate(x, y); p.rotate(rot)
            p.setBrush(QColor(farbe)); p.drawRoundedRect(QRectF(-g / 2, -g / 4, g, g / 2), 2, 2)
            p.restore()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Return, Qt.Key.Key_Enter, Qt.Key.Key_Space):
            self.close()


def main():
    args = sys.argv[1:]
    user = ich()
    heute = datetime.date.today()
    test = "--test" in args
    if test:
        rest = [a for a in args if a.isdigit()]
        alter = int(rest[0]) if rest else 7
    else:
        g = geburt(user)
        jahr = ist_dran(g, heute) if g else None
        if jahr is None:
            return 0
        alter = jahr - g[0]
        if alter < 1 or alter > 25:
            return 0
        m = merker(jahr)
        if os.path.exists(m):
            return 0
        try:
            os.makedirs(os.path.dirname(m), exist_ok=True)
            open(m, "w").write(heute.isoformat() + "\n")
        except OSError:
            pass
    app = QApplication(sys.argv)
    app.setDesktopFileName("pingulinux-geburtstag")
    name = vorname(user)
    w = Feier(name, alter)
    w.showFullScreen()
    QTimer.singleShot(800, lambda: sprich("Hallo %s! Alles Gute zum Geburtstag! Jetzt bist du %d!" % (name, alter)))
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
