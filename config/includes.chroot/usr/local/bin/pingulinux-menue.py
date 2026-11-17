#!/usr/bin/env python3
"""Auswahl-Menü mit KDE-Symbolen (für pd_menue_ikon in dialog.sh).

  pingulinux-menue.py TITEL TEXT tag symbol text [tag symbol text …]

Symbol: Name aus dem KDE-Symbolthema oder Pfad zu einer Bilddatei.

Gibt den Tag des gewählten Eintrags aus. Rückgabe 1 = abgebrochen.
TEXT darf einfache Auszeichnung (<b>, <big>, \\n) enthalten.
"""
import os
import sys

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QApplication, QDialog, QDialogButtonBox, QLabel, QListWidget,
                             QListWidgetItem, QVBoxLayout)

FENSTER_ICON = "/usr/share/pingulinux/icons/pingu.png"


def main():
    a = sys.argv[1:]
    if len(a) < 5 or (len(a) - 2) % 3:
        print(__doc__, file=sys.stderr)
        return 2
    titel, text, rest = a[0], a[1], a[2:]
    app = QApplication(sys.argv[:1])
    app.setDesktopFileName("pingulinux-kontrollzentrum")
    d = QDialog()
    d.setWindowTitle(titel)
    if os.path.exists(FENSTER_ICON):
        d.setWindowIcon(QIcon(FENSTER_ICON))
    v = QVBoxLayout(d)
    t = QLabel(text.replace("\\n", "<br>").replace("\n", "<br>"))
    t.setTextFormat(Qt.TextFormat.RichText)
    t.setWordWrap(True)
    v.addWidget(t)
    liste = QListWidget()
    liste.setIconSize(QSize(32, 32))
    liste.setSpacing(2)
    for i in range(0, len(rest), 3):
        tag, symbol, eintrag = rest[i:i + 3]
        ikon = QIcon(symbol) if symbol.startswith("/") else QIcon.fromTheme(symbol)   # Name oder Bilddatei
        it = QListWidgetItem(ikon, eintrag)
        it.setData(Qt.ItemDataRole.UserRole, tag)
        it.setSizeHint(QSize(0, 42))
        liste.addItem(it)
    liste.setCurrentRow(0)
    hoehe = min(42 * (len(rest) // 3) + 4 * (len(rest) // 3) + 12, 560)
    liste.setMinimumHeight(hoehe)
    v.addWidget(liste, 1)
    knoepfe = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
    knoepfe.button(QDialogButtonBox.StandardButton.Cancel).setText("Abbrechen")
    knoepfe.accepted.connect(d.accept)
    knoepfe.rejected.connect(d.reject)
    v.addWidget(knoepfe)
    liste.itemActivated.connect(lambda _it: d.accept())
    d.setMinimumWidth(520)
    if d.exec() != QDialog.DialogCode.Accepted or not liste.currentItem():
        return 1
    print(liste.currentItem().data(Qt.ItemDataRole.UserRole))
    return 0


if __name__ == "__main__":
    sys.exit(main())
