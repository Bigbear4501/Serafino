#!/usr/bin/env python3
"""Easter Egg: Fino fliegt über den Bildschirm und erzählt einen Witz.

Wird gestartet, wenn man Fino/Fino oben im Kontrollzentrum 5× schnell
antippt. Durchsichtiges Fenster über dem ganzen Bildschirm; ein Klick
irgendwo beendet es. Nach etwa 12 Sekunden ist Fino von selbst wieder weg.
"""
import math
import os
import random
import subprocess
import sys

from PyQt6.QtCore import Qt, QTimer, QElapsedTimer, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont, QPainterPath, QPen
from PyQt6.QtWidgets import QApplication, QWidget

FINO = "/usr/share/serafino/fino/fino.png"
WITZE = "/usr/share/serafino/fino/witze.txt"
DAUER_FLUG = 4.0      # Sekunden bis zur Mitte
DAUER_WITZ = 6.5      # Sekunden Sprechblase
DAUER_WEG = 2.0       # Sekunden wegfliegen


def witz():
    try:
        zeilen = [z.strip() for z in open(WITZE, encoding="utf-8")
                  if z.strip() and not z.startswith("#")]
    except OSError:
        zeilen = []
    z = random.choice(zeilen) if zeilen else "Hallo!|Schön, dass du da bist!"
    frage, _, antwort = z.partition("|")
    return frage, antwort


def sprich(text):
    for cmd in (["espeak-ng", "-v", "de", "-s", "150", text], ["spd-say", "-l", "de", text]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue


class Flug(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle("Fino")
        self.bild = QPixmap(FINO)
        self.frage, self.antwort = witz()
        self.uhr = QElapsedTimer()
        self.uhr.start()
        self.gesprochen = False
        t = QTimer(self)
        t.timeout.connect(self.tick)
        t.start(16)

    def tick(self):
        s = self.uhr.elapsed() / 1000.0
        if s > DAUER_FLUG + DAUER_WITZ + DAUER_WEG:
            self.close()
            return
        if s > DAUER_FLUG and not self.gesprochen:
            self.gesprochen = True
            sprich(self.frage + " ... " + self.antwort)
        self.update()

    def mousePressEvent(self, _):
        self.close()

    def keyPressEvent(self, _):
        self.close()

    def lage(self, s):
        """Position (Mitte von Fino) und Flügelschlag zur Zeit s."""
        w, h = self.width(), self.height()
        mitte = QPointF(w * 0.5, h * 0.45)
        if s < DAUER_FLUG:                         # von links unten hereinfliegen, Wellenlinie
            k = s / DAUER_FLUG
            k = 1 - (1 - k) ** 2                   # sanft abbremsen
            x = -150 + (mitte.x() + 150) * k
            y = h * 0.75 + (mitte.y() - h * 0.75) * k + math.sin(s * 5) * 40 * (1 - k)
        elif s < DAUER_FLUG + DAUER_WITZ:          # in der Mitte schweben
            x, y = mitte.x(), mitte.y() + math.sin(s * 2.5) * 10
        else:                                      # nach rechts oben davon
            k = (s - DAUER_FLUG - DAUER_WITZ) / DAUER_WEG
            x = mitte.x() + (w * 0.6) * k * k
            y = mitte.y() - (h * 0.7) * k * k
        flap = 1.0 + 0.08 * math.sin(s * 18)
        return QPointF(x, y), flap

    def paintEvent(self, _):
        s = self.uhr.elapsed() / 1000.0
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        pos, flap = self.lage(s)
        groesse = min(self.width(), self.height()) * 0.28
        bw = groesse * self.bild.width() / max(1, self.bild.height())
        p.save()
        p.translate(pos)
        p.rotate(math.sin(s * 3) * 6)
        p.scale(flap, 1 / flap)
        p.drawPixmap(QRectF(-bw / 2, -groesse / 2, bw, groesse), self.bild, QRectF(self.bild.rect()))
        p.restore()
        if DAUER_FLUG <= s < DAUER_FLUG + DAUER_WITZ:
            self.blase(p, pos, groesse, s - DAUER_FLUG)

    def blase(self, p, pos, groesse, t):
        f = QFont(self.font())
        f.setPointSizeF(max(14.0, self.height() / 45))
        p.setFont(f)
        breite = min(self.width() * 0.42, 620)
        text = self.frage + ("\n\n" + self.antwort if t > 2.8 else "")   # Antwort kommt nach einer Pause
        fl = Qt.TextFlag.TextWordWrap
        r = p.boundingRect(QRectF(0, 0, breite, 2000), fl, self.frage + "\n\n" + self.antwort)
        x = pos.x() + groesse * 0.45
        if x + r.width() + 40 > self.width():
            x = pos.x() - groesse * 0.45 - r.width() - 40
        y = pos.y() - groesse * 0.55 - r.height() / 2
        y = max(20, y)
        kasten = QRectF(x, y, r.width() + 40, r.height() + 32)
        pfad = QPainterPath()
        pfad.addRoundedRect(kasten, 22, 22)
        spitze = QPainterPath()
        sx = kasten.left() + 30 if kasten.left() > pos.x() else kasten.right() - 30
        spitze.moveTo(sx - 14, kasten.bottom() - 2)
        spitze.lineTo(pos.x() + (groesse * 0.2 if sx > pos.x() else -groesse * 0.2), pos.y() - groesse * 0.25)
        spitze.lineTo(sx + 14, kasten.bottom() - 2)
        spitze.closeSubpath()
        pfad = pfad.united(spitze)
        p.setPen(QPen(QColor("#1a4f7a"), 3))
        p.setBrush(QColor(255, 255, 255, 245))
        p.drawPath(pfad)
        p.setPen(QColor("#1d2329"))
        p.drawText(kasten.adjusted(20, 16, -20, -16), fl, text)


def main():
    if not os.path.exists(FINO):
        return 1
    app = QApplication(sys.argv)
    app.setDesktopFileName("serafino-fino")
    w = Flug()
    w.showFullScreen()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
