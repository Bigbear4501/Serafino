#!/usr/bin/env python3
"""serafino-programme.py - Programme pro Kind (bz3).

Kontrollzentrum → Benutzerkonten → „Programme pro Kind“.

Normalerweise entscheidet das Alter, welche Programme ein Kind starten darf.
Hier können Eltern für jedes Kind einzelne Programme davon abweichend
  • trotzdem erlauben (z. B. Krita schon mit 8) oder
  • sperren (z. B. ein Spiel nur für dieses Kind).
Alles andere bleibt „nach Alter“ – auch Programme, die später aus dem
App Store dazukommen.

Gespeichert wird über pkexec pingulinux-root-helper app-ausnahmen KIND
in /var/lib/pingulinux/app-ausnahmen/KIND.json. Danach läuft sofort die
Alters-Sperre (pingulinux-apply-all-ages.py) neu.
"""
import glob
import json
import os
import pwd
import shlex
import shutil
import subprocess
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
                             QComboBox, QHeaderView, QSplitter, QCheckBox, QMessageBox, QLineEdit)

FINO = "/usr/share/pingulinux/fino/fino.png"
PROFDIR = "/var/lib/pingulinux/profiles"
AUSNAHMEN = "/var/lib/pingulinux/app-ausnahmen"
SOURCES = ["/usr/share/pingulinux/app-ages.json", "/usr/share/pingulinux/store-apps.json"]
APPDIR = "/usr/share/applications"
FP_APPS = "/var/lib/flatpak/app"
FP_DESKTOP = "/var/lib/flatpak/exports/share/applications"
HELPER = ["pkexec", "/usr/local/bin/pingulinux-root-helper"]
PFAD = "/usr/bin:/usr/games:/usr/local/bin:/bin"

WAHL = [("alter", "Nach Alter"), ("erlauben", "Trotzdem erlauben"), ("sperren", "Sperren")]


def kinder():
    out = []
    try:
        namen = sorted(os.listdir(PROFDIR))
    except OSError:
        return out
    for n in namen:
        try:
            alter = int(open(os.path.join(PROFDIR, n)).read().strip())
            pw = pwd.getpwnam(n)
        except (OSError, ValueError, KeyError):
            continue
        out.append((n, pw.pw_gecos.split(",")[0] or n, alter))
    return out


def desktop_lesen(pfad):
    """Name (deutsch, wenn vorhanden), Symbol und Programm aus einer .desktop-Datei."""
    d = {}
    try:
        for z in open(pfad, encoding="utf-8", errors="replace"):
            z = z.strip()
            if z.startswith("[") and z != "[Desktop Entry]" and d:
                break
            for k in ("Name[de]", "Name", "Icon", "Exec", "NoDisplay"):
                if z.startswith(k + "=") and k not in d:
                    d[k] = z[len(k) + 1:]
    except OSError:
        pass
    return d


def programm_aus_exec(exec_zeile):
    try:
        teile = shlex.split(exec_zeile)
    except ValueError:
        return None
    while teile and (teile[0] == "env" or "=" in teile[0]):
        teile.pop(0)
    if not teile:
        return None
    exe = teile[0] if teile[0].startswith("/") else shutil.which(teile[0], path=PFAD)
    return os.path.realpath(exe) if exe else None


def programme():
    """Alle installierten Programme mit Altersgrenze: Liste von dicts
    (schluessel, name, ikon, ab)."""
    cmds, fps = {}, {}
    for src in SOURCES:
        try:
            eintraege = json.load(open(src, encoding="utf-8"))
        except Exception:
            continue
        for e in eintraege:
            if "min_age" not in e:
                continue
            if e.get("cmd"):
                alt = cmds.get(e["cmd"], {})
                cmds[e["cmd"]] = {"ab": e["min_age"], "name": e.get("name") or alt.get("name"),
                                  "ikon": e.get("icon") or alt.get("ikon")}
            if e.get("flatpak"):
                fps[e["flatpak"]] = {"ab": e["min_age"], "name": e.get("name"), "ikon": e.get("icon")}

    # Menü-Einträge: echtes Programm → (Name, Symbol)
    menue = {}
    for df in glob.glob(os.path.join(APPDIR, "*.desktop")):
        d = desktop_lesen(df)
        real = programm_aus_exec(d.get("Exec", ""))
        if real and real not in menue and d.get("NoDisplay", "").lower() != "true":
            menue[real] = (d.get("Name[de]") or d.get("Name"), d.get("Icon"))

    out = []
    for cmd, e in cmds.items():
        pfad = cmd if cmd.startswith("/") else shutil.which(cmd, path=PFAD)
        if not pfad or not os.path.exists(pfad):
            continue
        name, ikon = menue.get(os.path.realpath(pfad), (None, None))
        out.append({"schluessel": cmd, "name": name or e["name"] or cmd,
                    "ikon": ikon or e["ikon"] or "application-x-executable", "ab": e["ab"]})
    for ref, e in fps.items():
        if not os.path.isdir(os.path.join(FP_APPS, ref)):
            continue
        d = desktop_lesen(os.path.join(FP_DESKTOP, ref + ".desktop"))
        out.append({"schluessel": ref, "name": d.get("Name[de]") or d.get("Name") or e["name"] or ref,
                    "ikon": d.get("Icon") or e["ikon"] or "application-x-executable", "ab": e["ab"]})
    out.sort(key=lambda p: p["name"].lower())
    return out


def ausnahmen_lesen(kind):
    try:
        d = json.load(open(os.path.join(AUSNAHMEN, kind + ".json"), encoding="utf-8"))
        return set(d.get("erlauben", [])), set(d.get("sperren", []))
    except Exception:
        return set(), set()


class Fenster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Programme pro Kind")
        self.resize(900, 600)
        if os.path.exists(FINO):
            self.setWindowIcon(QIcon(FINO))
        self.kind = None
        self.alter = 0
        self.geaendert = False
        self.alle = programme()

        w = QWidget(); self.setCentralWidget(w)
        v = QVBoxLayout(w)
        v.setContentsMargins(18, 16, 18, 14)
        kopf = QHBoxLayout()
        ik = QLabel(); ik.setPixmap(QIcon.fromTheme("applications-other").pixmap(32, 32))
        kopf.addWidget(ik)
        titel = QLabel("Programme pro Kind")
        f = titel.font(); f.setPointSizeF(f.pointSizeF() * 1.35); f.setBold(True); titel.setFont(f)
        kopf.addWidget(titel); kopf.addStretch(1)
        v.addLayout(kopf)
        erkl = QLabel("Normalerweise entscheidet das Alter. Hier kannst du für ein Kind einzelne Programme "
                      "<b>trotzdem erlauben</b> oder <b>sperren</b>. Alles auf „Nach Alter“ bleibt wie bisher – "
                      "auch Programme, die später aus dem App Store dazukommen.")
        erkl.setWordWrap(True); erkl.setStyleSheet("color: palette(placeholder-text)")
        v.addWidget(erkl)

        split = QSplitter(); v.addWidget(split, 1)
        self.liste = QListWidget(); self.liste.setMinimumWidth(190)
        split.addWidget(self.liste)

        rechts = QWidget(); r = QVBoxLayout(rechts); r.setContentsMargins(8, 0, 0, 0)
        filt = QHBoxLayout()
        self.suche = QLineEdit(); self.suche.setPlaceholderText("Programm suchen …")
        self.suche.setClearButtonEnabled(True)
        self.suche.textChanged.connect(self.filtern)
        filt.addWidget(self.suche, 1)
        self.nur_aus = QCheckBox("Nur Ausnahmen zeigen")
        self.nur_aus.toggled.connect(self.filtern)
        filt.addWidget(self.nur_aus)
        r.addLayout(filt)

        self.tab = QTableWidget(0, 4)
        self.tab.setHorizontalHeaderLabels(["Programm", "Ab", "Nach Alter", "Für dieses Kind"])
        hh = self.tab.horizontalHeader()
        hh.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in (1, 2, 3):
            hh.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
        self.tab.verticalHeader().hide()
        self.tab.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tab.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        r.addWidget(self.tab, 1)

        unten = QHBoxLayout()
        self.status = QLabel("")
        self.status.setWordWrap(True)
        unten.addWidget(self.status, 1)
        self.zurueck = QPushButton(QIcon.fromTheme("edit-undo"), "Alles nach Alter")
        self.zurueck.clicked.connect(self.alles_nach_alter)
        unten.addWidget(self.zurueck)
        self.speichern = QPushButton(QIcon.fromTheme("document-save"), "Speichern")
        self.speichern.clicked.connect(self.sichern)
        unten.addWidget(self.speichern)
        r.addLayout(unten)
        split.addWidget(rechts)
        split.setStretchFactor(1, 1)

        self.kids = kinder()
        for n, voll, alter in self.kids:
            it = QListWidgetItem(QIcon.fromTheme("user-identity"), "%s (%d)" % (voll, alter))
            it.setData(Qt.ItemDataRole.UserRole, (n, alter))
            self.liste.addItem(it)
        self.liste.currentItemChanged.connect(self.kind_gewaehlt)
        if self.kids:
            self.liste.setCurrentRow(0)
        else:
            self.status.setText("Es gibt noch kein Kinderkonto. Lege es unter „Benutzerkonten“ an.")
            self.speichern.setEnabled(False); self.zurueck.setEnabled(False)

    # ---- Anzeige
    def kind_gewaehlt(self, it, vorher=None):
        if it is None:
            return
        if self.geaendert and vorher is not None:
            if QMessageBox.question(self, "Nicht gespeichert",
                                    "Die Änderungen für das vorige Kind sind noch nicht gespeichert. Verwerfen?") \
                    != QMessageBox.StandardButton.Yes:
                self.liste.blockSignals(True); self.liste.setCurrentItem(vorher); self.liste.blockSignals(False)
                return
        self.kind, self.alter = it.data(Qt.ItemDataRole.UserRole)
        erl, sp = ausnahmen_lesen(self.kind)
        self.tab.setRowCount(0)
        for p in self.alle:
            z = self.tab.rowCount(); self.tab.insertRow(z)
            name = QTableWidgetItem(QIcon.fromTheme(p["ikon"], QIcon.fromTheme("application-x-executable")),
                                    p["name"])
            name.setData(Qt.ItemDataRole.UserRole, p["schluessel"])
            name.setToolTip(p["schluessel"])
            self.tab.setItem(z, 0, name)
            ab = QTableWidgetItem("%d Jahre" % p["ab"]); ab.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.tab.setItem(z, 1, ab)
            frei = self.alter >= p["ab"]
            na = QTableWidgetItem(QIcon.fromTheme("dialog-ok-apply" if frei else "object-locked"),
                                  "erlaubt" if frei else "gesperrt")
            self.tab.setItem(z, 2, na)
            box = QComboBox()
            for wert, text in WAHL:
                box.addItem(text, wert)
            wahl = "sperren" if p["schluessel"] in sp else "erlauben" if p["schluessel"] in erl else "alter"
            box.setCurrentIndex([w for w, _ in WAHL].index(wahl))
            box.currentIndexChanged.connect(lambda _=0, b=box: self.wahl_geaendert(b))
            self.tab.setCellWidget(z, 3, box)
            self.faerben(box)
        self.geaendert = False
        self.filtern()
        self.zaehlen()

    def faerben(self, box):
        f = QFont(box.font()); f.setBold(box.currentData() != "alter"); box.setFont(f)

    def wahl_geaendert(self, box):
        self.faerben(box)
        self.geaendert = True
        self.zaehlen()
        if self.nur_aus.isChecked():
            self.filtern()

    def zeilen(self):
        for z in range(self.tab.rowCount()):
            yield z, self.tab.item(z, 0).data(Qt.ItemDataRole.UserRole), self.tab.cellWidget(z, 3)

    def filtern(self, *_):
        such = self.suche.text().strip().lower()
        for z, key, box in self.zeilen():
            name = self.tab.item(z, 0).text().lower()
            zeigen = (not such or such in name or such in key.lower()) and \
                     (not self.nur_aus.isChecked() or box.currentData() != "alter")
            self.tab.setRowHidden(z, not zeigen)

    def zaehlen(self):
        e = sum(1 for _, _, b in self.zeilen() if b.currentData() == "erlauben")
        s = sum(1 for _, _, b in self.zeilen() if b.currentData() == "sperren")
        if not e and not s:
            t = "Keine Ausnahmen – es gilt nur das Alter."
        else:
            t = "Ausnahmen: %d erlaubt, %d gesperrt." % (e, s)
        if self.geaendert:
            t += "  <b>Noch nicht gespeichert.</b>"
        self.status.setText(t)

    def alles_nach_alter(self):
        for _, _, box in self.zeilen():
            box.setCurrentIndex(0)

    # ---- Speichern
    def sichern(self):
        if not self.kind:
            return
        daten = {"erlauben": [], "sperren": []}
        for _, key, box in self.zeilen():
            if box.currentData() in daten:
                daten[box.currentData()].append(key)
        try:
            r = subprocess.run(HELPER + ["app-ausnahmen", self.kind], input=json.dumps(daten),
                               capture_output=True, text=True, timeout=300)
        except (OSError, subprocess.SubprocessError) as e:
            QMessageBox.warning(self, "Nicht gespeichert", str(e)); return
        if r.returncode in (126, 127):
            return                                   # Passwort-Fenster abgebrochen
        if r.returncode != 0:
            QMessageBox.warning(self, "Nicht gespeichert",
                                (r.stderr or r.stdout or "Unbekannter Fehler").strip()[-600:])
            return
        self.geaendert = False
        self.zaehlen()
        self.status.setText(self.status.text() + "  Gespeichert ✓ – gilt ab dem nächsten Start des Programms. "
                            "Im Menü erscheint es spätestens nach dem nächsten Anmelden.")

    def closeEvent(self, ev):
        if self.geaendert and QMessageBox.question(
                self, "Nicht gespeichert", "Die Änderungen sind noch nicht gespeichert. Trotzdem schließen?") \
                != QMessageBox.StandardButton.Yes:
            ev.ignore(); return
        ev.accept()


def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName("serafino-programme")
    f = Fenster(); f.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
