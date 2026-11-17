#!/usr/bin/env python3
"""pingulinux-einrichtung.py - Einrichtungs-Assistent nach der Installation (bz6).

  pingulinux-einrichtung.py --auto    beim Anmelden (Autostart): nur beim ersten
                                      Eltern-Anmelden nach der Installation
  pingulinux-einrichtung.py           jederzeit (Kontrollzentrum → Hilfe)

Schritte: Kinder anlegen → Kinderschutz-Filter → Bildschirmzeit → Fertig.
Alles hat sinnvolle Standardwerte: wer nichts ändert, klickt nur „Weiter“.
Geändert wird erst ganz am Ende („Einrichten“), mit einmal Eltern-Passwort.

Merker: /var/lib/pingulinux/einrichtung-fertig (fertig eingerichtet) bzw.
~/.local/state/pingulinux/einrichtung-spaeter („Später“ gedrückt).
"""
import datetime
import grp
import os
import pwd
import re
import subprocess
import sys
import threading

FERTIG = "/var/lib/pingulinux/einrichtung-fertig"
SPAETER = os.path.expanduser("~/.local/state/pingulinux/einrichtung-spaeter")
PROFDIR = "/var/lib/pingulinux/profiles"
HELPER = ["pkexec", "/usr/local/bin/pingulinux-root-helper"]
FINO = "/usr/share/pingulinux/fino/fino.png"
DNS_WAHL = "/etc/pingulinux/dns-provider"


def ist_live():
    try:
        return "boot=live" in open("/proc/cmdline").read().split()
    except OSError:
        return False


def ist_eltern():
    user = pwd.getpwuid(os.getuid()).pw_name
    if os.path.exists(os.path.join(PROFDIR, user)):
        return False
    try:
        return user in grp.getgrnam("sudo").gr_mem
    except KeyError:
        return False


def soll_automatisch():
    return (not ist_live() and ist_eltern()
            and not os.path.exists(FERTIG) and not os.path.exists(SPAETER))


# ------------------------------------------------------------------ Standardwerte
def alter(geburt, heute=None):
    heute = heute or datetime.date.today()
    return heute.year - geburt.year - ((heute.month, heute.day) < (geburt.month, geburt.day))


def zeit_standard(a):
    """(Minuten Mo–Fr, Minuten Sa–So, von, bis) – wie pingulinux-apply-age-profile.sh"""
    if a <= 6:
        return 45, 60, 8, 19
    if a <= 9:
        return 60, 90, 8, 20
    if a <= 12:
        return 90, 120, 7, 21
    if a <= 14:
        return 120, 180, 7, 21
    return 180, 240, 7, 22


def anmeldename(vorname, belegt):
    n = vorname.strip().lower()
    for a, b in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss"), (" ", "-")):
        n = n.replace(a, b)
    n = re.sub(r"[^a-z0-9_-]", "", n)
    n = re.sub(r"^[^a-z_]+", "", n)[:24] or "kind"
    kandidat, i = n, 2
    while kandidat in belegt:
        kandidat = "%s%d" % (n, i)
        i += 1
    return kandidat


def alle_konten():
    return {p.pw_name for p in pwd.getpwall()}


def dns_jetzt():
    try:
        w = open(DNS_WAHL).read().strip()
        if w in ("cleanbrowsing", "dns4eu", "off"):
            return w
    except OSError:
        pass
    try:
        r = open("/etc/resolv.conf").read()
        if "185.228.168.168" in r:
            return "cleanbrowsing"
        if "86.54.11.12" in r:
            return "dns4eu"
    except OSError:
        pass
    return "off"


# ------------------------------------------------------------------ Fenster
def main():
    if "--auto" in sys.argv and not soll_automatisch():
        return 0

    from PyQt6.QtCore import Qt, QDate, QTimer
    from PyQt6.QtGui import QIcon, QPixmap, QFont
    from PyQt6.QtWidgets import (QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
                                 QGridLayout, QLabel, QLineEdit, QDateEdit, QCheckBox, QPushButton,
                                 QListWidget, QListWidgetItem, QRadioButton, QButtonGroup,
                                 QSpinBox, QFrame, QMessageBox, QProgressBar, QWidget, QScrollArea)

    app = QApplication(sys.argv)
    app.setDesktopFileName("pingulinux-einrichtung")

    def ueberschrift(text):
        l = QLabel(text)
        f = l.font(); f.setPointSizeF(f.pointSizeF() * 1.3); f.setBold(True); l.setFont(f)
        l.setWordWrap(True)
        return l

    def text(t, leise=False):
        l = QLabel(t)
        l.setWordWrap(True)
        l.setTextFormat(Qt.TextFormat.RichText)
        if leise:
            l.setStyleSheet("color:palette(placeholder-text)")
        return l

    def ikon_zeile(ikon, t):
        h = QHBoxLayout()
        b = QLabel(); b.setPixmap(QIcon.fromTheme(ikon).pixmap(16, 16))
        h.addWidget(b, 0, Qt.AlignmentFlag.AlignTop)
        h.addWidget(text(t, leise=True), 1)
        return h

    neue_kinder = []          # dicts: vorname, name, geburt (date), ohne_pw, pw

    # ---------- 1. Willkommen
    class Willkommen(QWizardPage):
        def __init__(self):
            super().__init__()
            v = QVBoxLayout(self)
            h = QHBoxLayout()
            bild = QLabel()
            pm = QPixmap(FINO)
            if not pm.isNull():
                bild.setPixmap(pm.scaledToHeight(150, Qt.TransformationMode.SmoothTransformation))
            h.addWidget(bild)
            rechts = QVBoxLayout()
            rechts.addWidget(ueberschrift("Willkommen bei Serafino!"))
            rechts.addWidget(text(
                "Ich bin Fino und helfe euch in drei kurzen Schritten beim Einrichten:"
                "<ol><li>Kinderkonten anlegen</li><li>Kinderschutz-Filter fürs Internet</li>"
                "<li>Bildschirmzeit</li></ol>"
                "Alles ist schon sinnvoll voreingestellt. <b>Wer nichts ändern möchte, "
                "klickt einfach auf „Weiter“.</b>"))
            rechts.addStretch(1)
            h.addLayout(rechts, 1)
            v.addLayout(h)
            v.addStretch(1)
            v.addLayout(ikon_zeile("help-about", "Den Assistenten findet ihr jederzeit wieder im "
                                   "Eltern-Kontrollzentrum unter „Hilfe“. Alles lässt sich später "
                                   "auch dort ändern."))

    # ---------- 2. Kinder
    class Kinder(QWizardPage):
        def __init__(self):
            super().__init__()
            v = QVBoxLayout(self)
            v.addWidget(ueberschrift("Kinderkonten"))
            da = []
            try:
                da = sorted(os.listdir(PROFDIR))
            except OSError:
                pass
            if da:
                v.addWidget(text("Schon da: <b>%s</b>. Weitere Kinder könnt ihr hier hinzufügen." % ", ".join(da)))
            else:
                v.addWidget(text("Jedes Kind bekommt ein eigenes Konto. Das Alter bestimmt, welche "
                                 "Programme und Webseiten passen – das wächst automatisch mit."))
            form = QGridLayout()
            form.addWidget(QLabel("Vorname:"), 0, 0)
            self.vorname = QLineEdit(); self.vorname.setPlaceholderText("z. B. Lena")
            form.addWidget(self.vorname, 0, 1)
            form.addWidget(QLabel("Geburtstag:"), 1, 0)
            self.geburt = QDateEdit()
            self.geburt.setDisplayFormat("dd.MM.yyyy")
            self.geburt.setCalendarPopup(True)
            heute = QDate.currentDate()
            self.geburt.setDateRange(heute.addYears(-18), heute)
            self.geburt.setDate(heute.addYears(-5))
            self.geburt.dateChanged.connect(self.alter_geaendert)
            form.addWidget(self.geburt, 1, 1)
            self.alter_lbl = QLabel()
            form.addWidget(self.alter_lbl, 1, 2)
            self.ohne = QCheckBox("Ohne Passwort anmelden (für die Kleinen bis 6 Jahre)")
            self.ohne.toggled.connect(self.pw_zeigen)
            form.addWidget(self.ohne, 2, 1, 1, 2)
            form.addWidget(QLabel("Passwort:"), 3, 0)
            self.pw1 = QLineEdit(); self.pw1.setEchoMode(QLineEdit.EchoMode.Password)
            form.addWidget(self.pw1, 3, 1)
            form.addWidget(QLabel("Wiederholen:"), 4, 0)
            self.pw2 = QLineEdit(); self.pw2.setEchoMode(QLineEdit.EchoMode.Password)
            form.addWidget(self.pw2, 4, 1)
            self.dazu = QPushButton(QIcon.fromTheme("list-add"), "Kind hinzufügen")
            self.dazu.clicked.connect(self.hinzufuegen)
            form.addWidget(self.dazu, 5, 1)
            v.addLayout(form)
            v.addWidget(text("<b>Neu angelegt werden:</b>"))
            self.liste = QListWidget()
            self.liste.setMinimumHeight(90)
            v.addWidget(self.liste, 1)
            weg = QPushButton(QIcon.fromTheme("list-remove"), "Aus der Liste nehmen")
            weg.clicked.connect(self.entfernen)
            v.addWidget(weg, 0, Qt.AlignmentFlag.AlignLeft)
            v.addLayout(ikon_zeile("help-hint", "Ohne Kinder weiterklicken geht auch – Konten lassen "
                                   "sich jederzeit im Kontrollzentrum unter „Benutzerkonten“ anlegen."))
            self.alter_geaendert()

        def alter_jetzt(self):
            return alter(self.geburt.date().toPyDate())

        def alter_geaendert(self):
            a = self.alter_jetzt()
            self.alter_lbl.setText("%d Jahr%s" % (a, "" if a == 1 else "e"))
            klein = a <= 6
            self.ohne.setEnabled(klein)
            self.ohne.setChecked(klein)
            self.pw_zeigen()

        def pw_zeigen(self):
            an = not self.ohne.isChecked()
            self.pw1.setEnabled(an); self.pw2.setEnabled(an)

        def hinzufuegen(self):
            vn = self.vorname.text().strip()
            if not vn:
                QMessageBox.information(self, "Kinderkonten", "Bitte einen Vornamen eintragen.")
                return
            ohne = self.ohne.isChecked() and self.ohne.isEnabled()
            if not ohne:
                if not self.pw1.text():
                    QMessageBox.information(self, "Kinderkonten",
                                            "Bitte ein Passwort für %s eintragen – oder bei Kindern "
                                            "bis 6 „Ohne Passwort“ wählen." % vn)
                    return
                if self.pw1.text() != self.pw2.text():
                    QMessageBox.information(self, "Kinderkonten", "Die beiden Passwörter sind nicht gleich.")
                    return
            belegt = alle_konten() | {k["name"] for k in neue_kinder}
            k = {"vorname": vn, "name": anmeldename(vn, belegt), "geburt": self.geburt.date().toPyDate(),
                 "ohne_pw": ohne, "pw": "" if ohne else self.pw1.text()}
            k["alter"] = alter(k["geburt"])
            wd, we, von, bis = zeit_standard(k["alter"])
            k.update(wd=wd, we=we, von=von, bis=bis)
            neue_kinder.append(k)
            it = QListWidgetItem(QIcon.fromTheme("im-user"),
                                 "%s – %d Jahre – Anmeldename „%s“ – %s" % (
                                     vn, k["alter"], k["name"], "ohne Passwort" if ohne else "mit Passwort"))
            self.liste.addItem(it)
            self.vorname.clear(); self.pw1.clear(); self.pw2.clear()
            self.vorname.setFocus()

        def entfernen(self):
            r = self.liste.currentRow()
            if r >= 0:
                self.liste.takeItem(r)
                del neue_kinder[r]

        def validatePage(self):
            if self.vorname.text().strip():
                ja = QMessageBox.question(self, "Kinderkonten",
                                          "„%s“ steht noch im Feld, ist aber nicht hinzugefügt. "
                                          "Jetzt hinzufügen?" % self.vorname.text().strip())
                if ja == QMessageBox.StandardButton.Yes:
                    n = len(neue_kinder)
                    self.hinzufuegen()
                    return len(neue_kinder) > n
            return True

    # ---------- 3. Filter
    class Filter(QWizardPage):
        def __init__(self):
            super().__init__()
            v = QVBoxLayout(self)
            v.addWidget(ueberschrift("Kinderschutz-Filter"))
            v.addWidget(text("Der Filter sperrt Seiten mit Erwachsenen- und Gewaltinhalten für den "
                             "ganzen Computer – in jedem Programm und für alle Konten. "
                             "Zusätzlich sperrt Serafino soziale Netzwerke für Kinder unter 13."))
            self.gruppe = QButtonGroup(self)
            self.knoepfe = {}
            for wert, titel, unter in (
                    ("cleanbrowsing", "CleanBrowsing Family (empfohlen)",
                     "Bewährter Familienfilter, Dienst aus den USA."),
                    ("dns4eu", "DNS4EU Kinderschutz",
                     "Europäischer Dienst, EU-Datenschutz. Noch recht neu."),
                    ("off", "Aus",
                     "Keine Filterung. Nur empfehlenswert, wenn ihr einen eigenen Filter im Router nutzt.")):
                rb = QRadioButton(titel)
                f = rb.font(); f.setBold(True); rb.setFont(f)
                self.gruppe.addButton(rb)
                self.knoepfe[wert] = rb
                v.addSpacing(6)
                v.addWidget(rb)
                u = text(unter, leise=True); u.setContentsMargins(26, 0, 0, 0)
                v.addWidget(u)
            self.jetzt = dns_jetzt()
            self.knoepfe.get(self.jetzt, self.knoepfe["cleanbrowsing"]).setChecked(True)
            v.addStretch(1)
            v.addLayout(ikon_zeile("security-high", "Der Filter arbeitet über DNS: Er sieht nur, welche "
                                   "Seite aufgerufen wird, nicht was darauf passiert."))

        def wahl(self):
            for w, rb in self.knoepfe.items():
                if rb.isChecked():
                    return w
            return self.jetzt

    # ---------- 4. Bildschirmzeit
    class Zeit(QWizardPage):
        def __init__(self):
            super().__init__()
            self.v = QVBoxLayout(self)
            self.v.addWidget(ueberschrift("Bildschirmzeit"))
            self.inhalt = QWidget()
            sc = QScrollArea(); sc.setWidgetResizable(True); sc.setFrameShape(QFrame.Shape.NoFrame)
            sc.setWidget(self.inhalt)
            self.v.addWidget(sc, 1)
            self.v.addLayout(ikon_zeile("preferences-system-time",
                                        "Ist die Zeit um, meldet sich das Konto ab – Fino sagt vorher "
                                        "Bescheid. „+15 Min.“ für heute und alles andere geht im "
                                        "Kontrollzentrum unter „Bildschirmzeit“."))
            self.felder = []

        def initializePage(self):
            alt = self.inhalt.layout()
            if alt:
                QWidget().setLayout(alt)          # altes Layout wegwerfen
            g = QGridLayout(self.inhalt)
            self.felder = []
            if not neue_kinder:
                g.addWidget(text("Keine neuen Kinderkonten – hier gibt es nichts einzustellen.<br>"
                                 "Bestehende Konten behalten ihre Zeiten."), 0, 0)
                g.setRowStretch(1, 1)
                return
            g.addWidget(text("Vorgeschlagen nach dem Alter. Zum Übernehmen einfach „Weiter“."), 0, 0, 1, 6)
            for c, t in enumerate(["", "Mo–Fr", "Sa–So", "erlaubt von", "bis", ""]):
                if t:
                    g.addWidget(text("<b>%s</b>" % t), 1, c)
            for i, k in enumerate(neue_kinder, start=2):
                g.addWidget(QLabel("%s (%d)" % (k["vorname"], k["alter"])), i, 0)
                wd = QSpinBox(); wd.setRange(10, 600); wd.setSingleStep(15); wd.setSuffix(" Min."); wd.setValue(k["wd"])
                we = QSpinBox(); we.setRange(10, 600); we.setSingleStep(15); we.setSuffix(" Min."); we.setValue(k["we"])
                von = QSpinBox(); von.setRange(0, 23); von.setSuffix(" Uhr"); von.setValue(k["von"])
                bis = QSpinBox(); bis.setRange(1, 24); bis.setSuffix(" Uhr"); bis.setValue(k["bis"])
                for c, w in enumerate((wd, we, von, bis), start=1):
                    g.addWidget(w, i, c)
                self.felder.append((k, wd, we, von, bis))
            g.setColumnStretch(5, 1)
            g.setRowStretch(len(neue_kinder) + 2, 1)

        def validatePage(self):
            for k, wd, we, von, bis in self.felder:
                if von.value() >= bis.value():
                    QMessageBox.information(self, "Bildschirmzeit",
                                            "Bei %s liegt „von“ nicht vor „bis“." % k["vorname"])
                    return False
            for k, wd, we, von, bis in self.felder:
                k.update(wd=wd.value(), we=we.value(), von=von.value(), bis=bis.value())
            return True

    # ---------- 5. Fertig
    class Fertig(QWizardPage):
        def __init__(self, filter_seite):
            super().__init__()
            self.filter_seite = filter_seite
            v = QVBoxLayout(self)
            v.addWidget(ueberschrift("Alles bereit"))
            self.zusammen = text("")
            v.addWidget(self.zusammen)
            v.addStretch(1)
            self.balken = QProgressBar(); self.balken.hide()
            v.addWidget(self.balken)
            self.status = text("", leise=True)
            v.addWidget(self.status)
            self.erledigt = False

        def initializePage(self):
            zeilen = []
            if neue_kinder:
                for k in neue_kinder:
                    zeilen.append("<li><b>%s</b> (%d Jahre, Anmeldename „%s“, %s) – Bildschirmzeit "
                                  "%d Min. Mo–Fr, %d Min. Sa–So, %d–%d Uhr</li>" % (
                                      k["vorname"], k["alter"], k["name"],
                                      "ohne Passwort" if k["ohne_pw"] else "mit Passwort",
                                      k["wd"], k["we"], k["von"], k["bis"]))
            else:
                zeilen.append("<li>Keine neuen Kinderkonten</li>")
            namen = {"cleanbrowsing": "CleanBrowsing Family", "dns4eu": "DNS4EU Kinderschutz", "off": "aus"}
            w = self.filter_seite.wahl()
            zeilen.append("<li>Kinderschutz-Filter: <b>%s</b>%s</li>" % (
                namen[w], "" if w != self.filter_seite.jetzt else " (bleibt wie er ist)"))
            self.zusammen.setText("Mit „Einrichten“ wird Folgendes eingestellt:<ul>%s</ul>"
                                  "Dafür wird einmal das Eltern-Passwort gebraucht." % "".join(zeilen))

        def validatePage(self):
            if self.erledigt:
                return True
            self.schritte = []
            for k in neue_kinder:
                modus = "ohne" if k["ohne_pw"] else "pw"
                self.schritte.append(("Konto für %s anlegen" % k["vorname"],
                                      HELPER + ["konto-neu", k["name"], k["geburt"].isoformat(), "", modus],
                                      k["pw"] if modus == "pw" else None))
                wd0, we0, von0, bis0 = zeit_standard(k["alter"])
                if (k["wd"], k["we"]) != (wd0, we0):
                    self.schritte.append(("Bildschirmzeit für %s" % k["vorname"],
                                          HELPER + ["tk-limits", k["name"], str(k["wd"] * 60), str(k["we"] * 60)], None))
                if (k["von"], k["bis"]) != (von0, bis0):
                    self.schritte.append(("Uhrzeiten für %s" % k["vorname"],
                                          HELPER + ["tk-hours", k["name"],
                                                    ";".join(str(h) for h in range(k["von"], k["bis"]))], None))
            w = self.filter_seite.wahl()
            if w != self.filter_seite.jetzt:
                self.schritte.append(("Kinderschutz-Filter umstellen", HELPER + ["dns", w], None))
            self.schritte.append(("Abschließen", HELPER + ["einrichtung-fertig"], None))
            self.fehler = []
            self.nr = 0
            self.balken.setRange(0, len(self.schritte)); self.balken.setValue(0); self.balken.show()
            self.wizard().button(QWizard.WizardButton.FinishButton).setEnabled(False)
            self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)
            self.naechster()
            return False

        def naechster(self):
            if self.nr >= len(self.schritte):
                return self.ende()
            titel, cmd, eingabe = self.schritte[self.nr]
            self.status.setText(titel + " …")
            self.ergebnis = None

            def lauf():
                try:
                    r = subprocess.run(cmd, input=eingabe, capture_output=True, text=True)
                    self.ergebnis = (r.returncode, (r.stderr or r.stdout).strip())
                except OSError as e:
                    self.ergebnis = (127, str(e))
            threading.Thread(target=lauf, daemon=True).start()
            self.warten()

        def warten(self):
            if self.ergebnis is None:
                QTimer.singleShot(200, self.warten)
                return
            rc, meldung = self.ergebnis
            titel = self.schritte[self.nr][0]
            if rc in (126, 127) and self.nr == 0:      # Passwort-Fenster abgebrochen
                self.status.setText("Abgebrochen – es wurde nichts geändert.")
                self.balken.hide()
                self.wizard().button(QWizard.WizardButton.FinishButton).setEnabled(True)
                self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(True)
                return
            if rc != 0:
                self.fehler.append("%s: %s" % (titel, meldung.splitlines()[-1] if meldung else "Fehler %d" % rc))
            self.nr += 1
            self.balken.setValue(self.nr)
            self.naechster()

        def ende(self):
            self.erledigt = True
            self.wizard().button(QWizard.WizardButton.BackButton).setEnabled(False)
            self.wizard().button(QWizard.WizardButton.CancelButton).setEnabled(False)
            fb = self.wizard().button(QWizard.WizardButton.FinishButton)
            fb.setEnabled(True)
            fb.setText("Schließen")
            if self.fehler:
                self.status.setText("<b>Nicht alles hat geklappt:</b><br>" + "<br>".join(self.fehler) +
                                    "<br>Das lässt sich im Kontrollzentrum nachholen.")
            else:
                self.status.setText("<b>Fertig!</b> Viel Spaß mit Serafino. Die Kinder können sich "
                                    "jetzt am Anmeldebildschirm anmelden.")

    w = QWizard()
    w.setWindowTitle("Serafino einrichten")
    w.setWindowIcon(QIcon.fromTheme("tools-wizard"))
    w.setWizardStyle(QWizard.WizardStyle.ClassicStyle)
    w.setOption(QWizard.WizardOption.NoBackButtonOnStartPage, True)
    w.setButtonText(QWizard.WizardButton.NextButton, "Weiter")
    w.setButtonText(QWizard.WizardButton.BackButton, "Zurück")
    w.setButtonText(QWizard.WizardButton.FinishButton, "Einrichten")
    w.setButtonText(QWizard.WizardButton.CancelButton, "Später")
    filt = Filter()
    for seite in (Willkommen(), Kinder(), filt, Zeit(), Fertig(filt)):
        w.addPage(seite)
    w.resize(720, 560)

    def abbrechen():
        if "--auto" in sys.argv:
            try:
                os.makedirs(os.path.dirname(SPAETER), exist_ok=True)
                open(SPAETER, "w").close()
            except OSError:
                pass
            QMessageBox.information(w, "Serafino einrichten",
                                    "Kein Problem! Den Assistenten findest du jederzeit im "
                                    "Eltern-Kontrollzentrum unter „Hilfe“.")
    w.rejected.connect(abbrechen)
    w.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
