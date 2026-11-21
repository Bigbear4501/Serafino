#!/usr/bin/env python3
"""Serafino „Hardware & Treiber“ (bz14) – wie „Zusätzliche Treiber“ bei Ubuntu.

Erkennt (ohne Passwort): Grafikkarten, WLAN, laufenden Kernel, Secure Boot.
Bietet an: Nvidia-Treiber, Broadcom-WLAN (broadcom-sta), neuer Kernel mit
Firmware aus Backports – installieren, entfernen, wechseln.
„Änderungen anwenden“ fragt einmal nach dem Eltern-Passwort und ruft
  pkexec serafino-root-helper treiber nvidia=… broadcom=… kernel=…
auf. Vorher legt das Root-Skript eine Sicherung an. Danach: Neustart-Hinweis,
bei Secure Boot mit Code für den blauen MOK-Bildschirm.
"""
import os
import re
import subprocess
import sys

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QRadioButton, QButtonGroup, QScrollArea,
                             QProgressBar, QMessageBox, QFrame)

HELPER = "/usr/local/bin/serafino-root-helper"
LOGO = "/usr/share/serafino/fino/fino.png"
LOG = "/var/log/serafino-treiber.log"

# Broadcom-Chips, die nur mit „wl“ (broadcom-sta) laufen oder damit besser.
# Nur angeboten, wenn der Chip gerade OHNE Treiber dasteht.
BROADCOM_WL = {"4311", "4312", "4313", "4315", "4327", "4328", "4329", "432a", "432b", "432c", "432d",
               "4331", "4353", "4357", "4358", "4359", "4360", "4365", "43a0", "43b1", "a8d6", "a8d8",
               "a99d", "43a9", "43aa", "43b2"}


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def is_live():
    try:
        return "boot=live" in open("/proc/cmdline").read()
    except OSError:
        return False


def installiert(pkg):
    out = run(["dpkg-query", "-W", "-f=${Status}", pkg])
    return "install ok installed" in out


def pci_geraete():
    """Liste von Dicts: klasse, klassen_id, name, vendor, device, treiber."""
    geraete, akt = [], None
    for z in run(["lspci", "-nnk"]).splitlines():
        m = re.match(r"^\S+\s+(.+?) \[([0-9a-f]{4})\]: (.+) \[([0-9a-f]{4}):([0-9a-f]{4})\]", z)
        if m:
            akt = {"klasse": m.group(1), "klassen_id": m.group(2), "name": m.group(3),
                   "vendor": m.group(4), "device": m.group(5), "treiber": None}
            geraete.append(akt)
        elif akt and "Kernel driver in use:" in z:
            akt["treiber"] = z.split(":", 1)[1].strip()
    return geraete


def secure_boot():
    out = run(["mokutil", "--sb-state"]).lower()
    if "enabled" in out:
        return True
    if "disabled" in out:
        return False
    try:   # ohne mokutil: EFI-Variable direkt lesen
        for f in os.listdir("/sys/firmware/efi/efivars"):
            if f.startswith("SecureBoot-"):
                return open(os.path.join("/sys/firmware/efi/efivars", f), "rb").read()[-1] == 1
    except OSError:
        pass
    return None


def backports_kernel_version():
    """Version von linux-image-amd64 in trixie-backports (oder None)."""
    zeilen = run(["apt-cache", "policy", "linux-image-amd64"]).splitlines()
    letzte = None
    for z in zeilen:
        m = re.match(r"^\s+(?:\*\*\*\s+)?(\S+)\s+-?\d+$", z)
        if m:
            letzte = m.group(1)
        elif "trixie-backports" in z and letzte:
            return letzte
    return None


def mok_offen():
    """Secure Boot an, eigene Treiber (DKMS) da, Schlüssel aber noch nicht bestätigt?"""
    key = "/var/lib/dkms/mok.pub"
    if not installiert("dkms") or not os.path.exists(key):
        return False
    return "already enrolled" not in run(["mokutil", "--test-key", key]).lower()


def backports_quelle():
    """Ist trixie-backports als Paketquelle eingetragen?"""
    import glob as _g
    for f in ["/etc/apt/sources.list"] + _g.glob("/etc/apt/sources.list.d/*"):
        try:
            for z in open(f, encoding="utf-8", errors="replace"):
                if "trixie-backports" in z and not z.lstrip().startswith("#"):
                    return True
        except OSError:
            continue
    return False


def bpo_kernel_pakete():
    """Installierte Kernel-Pakete aus Backports. Erkennbar an der VERSION („~bpo13“) –
    der Name (z. B. linux-image-7.2.12+deb13-amd64) verrät es seit Debian 13 nicht mehr."""
    out = run(["dpkg-query", "-W", "-f=${Package} ${Version} ${Status}\\n", "linux-image-[0-9]*"])
    pakete = []
    for z in out.splitlines():
        t = z.split(" ", 2)
        if len(t) == 3 and "bpo" in t[1] and "install ok installed" in t[2]:
            pakete.append(t[0])
    return pakete


def bpo_kernel_installiert():
    return bool(bpo_kernel_pakete())


def bpo_laeuft_gerade():
    """Läuft gerade ein Backports-Kernel? (Paket zum laufenden Kernel hat „bpo“ in der Version)"""
    return "linux-image-" + os.uname().release in bpo_kernel_pakete()


def kurz_version(v):
    """6.16.3-1~bpo13+1 → 6.16"""
    m = re.match(r"(\d+\.\d+)", v or "")
    return m.group(1) if m else (v or "?")


class Arbeiter(QThread):
    zeile = pyqtSignal(str)
    fertig = pyqtSignal(int)

    def __init__(self, args):
        super().__init__()
        self.args = args

    def run(self):
        try:
            p = subprocess.Popen(["pkexec", HELPER, "treiber"] + self.args, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True, bufsize=1)
        except OSError:
            self.fertig.emit(127)
            return
        for z in p.stdout:
            self.zeile.emit(z.rstrip("\n"))
        self.fertig.emit(p.wait())


class IkonText(QWidget):
    """Statuszeile: KDE-Symbol links, Text rechts (statt Emojis im Text)."""
    def __init__(self):
        super().__init__()
        h = QHBoxLayout(self)
        h.setContentsMargins(0, 0, 0, 0)
        self.bild = QLabel()
        self.bild.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bild.hide()
        self.txt = QLabel("")
        self.txt.setWordWrap(True)
        h.addWidget(self.bild)
        h.addWidget(self.txt, 1)

    def setText(self, t, ikon=None):
        self.txt.setText(t)
        if ikon:
            self.bild.setPixmap(QIcon.fromTheme(ikon).pixmap(16, 16))
            self.bild.show()
        else:
            self.bild.hide()

    def text(self):
        return self.txt.text()


class Fenster(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hardware & Treiber")
        self.resize(760, 680)
        if os.path.exists(LOGO):
            self.setWindowIcon(QIcon(LOGO))
        self.live = is_live()
        self.wahl = {}            # name -> (QButtonGroup, {id: wert}, startwert)
        self.mok_code = None
        self.neustart = False
        self.hinweise = []

        zentral = QWidget()
        self.setCentralWidget(zentral)
        aussen = QVBoxLayout(zentral)
        kopf_zeile = QHBoxLayout()
        kopf_ikon = QLabel()
        kopf_ikon.setPixmap(QIcon.fromTheme("hwinfo", QIcon.fromTheme("cpu")).pixmap(48, 48))
        kopf_ikon.setAlignment(Qt.AlignmentFlag.AlignTop)
        kopf_zeile.addWidget(kopf_ikon)
        kopf = QLabel("<big><b>Hardware & Treiber</b></big><br>"
                      "Serafino bringt freie Treiber für fast alles schon mit. Hier gibt es "
                      "Zusätze für Geräte, die damit nicht (gut) laufen.")
        kopf.setWordWrap(True)
        kopf_zeile.addWidget(kopf, 1)
        aussen.addLayout(kopf_zeile)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        innen = QWidget()
        self.liste = QVBoxLayout(innen)
        scroll.setWidget(innen)
        aussen.addWidget(scroll, 1)

        self.status = IkonText()
        aussen.addWidget(self.status)
        self.balken = QProgressBar()
        self.balken.setRange(0, 0)
        self.balken.hide()
        aussen.addWidget(self.balken)
        knoepfe = QHBoxLayout()
        knoepfe.addStretch(1)
        self.zu = QPushButton("Schließen")
        self.zu.clicked.connect(self.close)
        self.los = QPushButton(QIcon.fromTheme("dialog-ok-apply"), "Änderungen anwenden")
        self.los.setEnabled(False)
        self.los.clicked.connect(self.anwenden)
        knoepfe.addWidget(self.zu)
        knoepfe.addWidget(self.los)
        aussen.addLayout(knoepfe)

        self.aufbauen()

    # ---------- Erkennung und Anzeige ----------
    def gruppe(self, titel, ikon=None):
        zeile = QHBoxLayout()
        if ikon:
            bild = QLabel()
            bild.setPixmap(QIcon.fromTheme(ikon).pixmap(22, 22))
            zeile.addWidget(bild)
        kopf = QLabel(titel)
        f = kopf.font(); f.setBold(True); f.setPointSizeF(f.pointSizeF() * 1.1); kopf.setFont(f)
        zeile.addWidget(kopf, 1)
        self.liste.addSpacing(6)
        self.liste.addLayout(zeile)
        box = QFrame()
        box.setFrameShape(QFrame.Shape.StyledPanel)
        v = QVBoxLayout(box)
        self.liste.addWidget(box)
        return v

    def text(self, layout, t, klein=False, ikon=None):
        l = QLabel(t)
        l.setWordWrap(True)
        l.setTextFormat(Qt.TextFormat.RichText)
        f = l.font(); f.setBold(False)
        if klein:
            f.setPointSizeF(f.pointSizeF() * 0.92)
        l.setFont(f)
        if ikon:                      # KDE-Symbol links neben dem Text
            zeile = QHBoxLayout()
            bild = QLabel()
            bild.setPixmap(QIcon.fromTheme(ikon).pixmap(16, 16))
            bild.setAlignment(Qt.AlignmentFlag.AlignTop)
            zeile.addWidget(bild)
            zeile.addWidget(l, 1)
            layout.addLayout(zeile)
        else:
            layout.addWidget(l)
        return l

    def optionen(self, layout, name, eintraege, start):
        """eintraege: [(wert, text)], start: aktueller wert."""
        g = QButtonGroup(self)
        werte = {}
        for i, (wert, t) in enumerate(eintraege):
            r = QRadioButton(t)
            f = r.font(); f.setBold(False); r.setFont(f)
            r.setChecked(wert == start)
            r.setEnabled(not self.live)
            g.addButton(r, i)
            werte[i] = wert
            layout.addWidget(r)
        g.idToggled.connect(self.geaendert)
        self.wahl[name] = (g, werte, start)

    def aufbauen(self):
        geraete = pci_geraete()
        sb = secure_boot()

        # --- Grafik ---
        v = self.gruppe("Grafik", "video-display")
        grafik = [g for g in geraete if g["klassen_id"] in ("0300", "0302", "0380")]
        if not grafik:
            self.text(v, "Keine Grafikkarte erkannt.")
        nvidia = [g for g in grafik if g["vendor"] == "10de"]
        for g in grafik:
            tr = g["treiber"] or "kein Treiber"
            self.text(v, "<b>%s</b><br><span style='color:gray'>Treiber: %s</span>" % (g["name"], tr))
        if nvidia:
            nv_an = installiert("nvidia-driver") or installiert("nvidia-tesla-535-driver")
            self.optionen(v, "nvidia", [
                ("aus", "Freier Treiber (nouveau) – schon dabei, für Lernspiele und Videos meist ausreichend"),
                ("an", "Nvidia-Treiber (von Nvidia, nicht frei) – schneller bei 3D-Spielen; "
                       "Serafino wählt die passende Version")], "an" if nv_an else "aus")
            self.text(v, "<b>Experimentell:</b> Der Nvidia-Treiber ist noch nicht auf echter Hardware getestet. "
                         "Vorher wird eine Sicherung angelegt – läuft danach etwas nicht, hilft "
                         "Kontrollzentrum → Sicherung → „Gestern wiederherstellen“.", klein=True,
                      ikon="applications-science")
            if any(g["vendor"] in ("8086", "1002") for g in grafik):
                self.text(v, "Dieser Computer hat zwei Grafikchips. Der Bildschirm läuft über den sparsamen "
                             "Chip, die Nvidia-Karte hilft bei Spielen: im Startmenü Rechtsklick auf das Spiel → "
                             "„Mit dedizierter Grafikkarte starten“ (geht nach der Installation des Nvidia-Treibers).",
                          klein=True, ikon="help-hint")
            self.text(v, "Sehr alte Nvidia-Karten (etwa vor 2014) unterstützt Debian 13 nicht mehr – "
                         "dann bleibt der freie Treiber.", klein=True)
        elif grafik:
            self.text(v, "Läuft mit dem freien Treiber. Nichts zu tun.", ikon="data-success")

        # --- WLAN ---
        v = self.gruppe("WLAN", "network-wireless")
        netz = [g for g in geraete if g["klassen_id"] == "0280"]
        if not netz:
            self.text(v, "Kein eingebautes WLAN erkannt (USB-WLAN-Sticks erscheinen hier nicht).")
        broadcom_offen = False
        for g in netz:
            tr = g["treiber"]
            self.text(v, "<b>%s</b><br><span style='color:gray'>Treiber: %s</span>"
                      % (g["name"], tr or "<b>keiner – WLAN geht so nicht</b>"))
            if g["vendor"] == "14e4" and (g["device"] in BROADCOM_WL or not tr or tr == "wl"):
                broadcom_offen = True
        bc_an = installiert("broadcom-sta-dkms")
        if broadcom_offen or bc_an:
            self.optionen(v, "broadcom", [
                ("aus", "Ohne Zusatz-Treiber (freie Treiber aus dem Kernel)"),
                ("an", "Broadcom-WLAN-Treiber „wl“ (broadcom-sta, nicht frei)")], "an" if bc_an else "aus")
            self.text(v, "<b>Experimentell:</b> Der Broadcom-Treiber ist noch nicht auf echter Hardware getestet. "
                         "Vorher wird eine Sicherung angelegt – läuft danach etwas nicht, hilft "
                         "Kontrollzentrum → Sicherung → „Gestern wiederherstellen“.", klein=True,
                      ikon="applications-science")
            self.text(v, "Zum Installieren braucht der Computer kurz Internet – zum Beispiel per "
                         "Netzwerkkabel oder Handy über USB (USB-Tethering).", klein=True)
        elif netz:
            self.text(v, "Läuft. Nichts zu tun.", ikon="data-success")

        # --- Kernel ---
        v = self.gruppe("Kernel (Herzstück des Systems)", "preferences-system")
        laeuft = os.uname().release
        bpo_laeuft = bpo_laeuft_gerade()
        bpo_da = bpo_laeuft or bpo_kernel_installiert()   # zählt schon, bevor neu gestartet wurde
        bpo_ver = backports_kernel_version()
        self.text(v, "Läuft gerade: <b>%s</b>%s" % (laeuft, " (aus Backports)" if bpo_laeuft else " (Debian 13)"))
        if bpo_da and not bpo_laeuft:
            self.text(v, "Der neuere Kernel ist installiert und startet nach dem nächsten Neustart. "
                         "Zurück zu Debian 13 geht auch schon jetzt.", klein=True, ikon="system-reboot")
        if os.path.exists("/var/lib/serafino/kernel-aufraeumen"):
            self.text(v, "Wechsel zurück auf Debian 13 ist vorgemerkt – bitte neu starten.", ikon="system-reboot")
        # Immer anbieten: Fehlt die Version (Paketliste noch nie geholt, z. B. gleich nach der
        # Installation), holt das Anwenden sie selbst – und trägt Backports ein, falls nötig.
        ver = ("Neuerer Kernel %s" % kurz_version(bpo_ver)) if bpo_ver else "Neuerer Kernel"
        eintraege = [("debian", "Debian 13 (stabil, empfohlen)"),
                     ("bpo", "%s mit neuer Firmware aus Backports – für sehr neue Geräte "
                             "(WLAN, Ton, Touch, Akku)" % ver)]
        self.optionen(v, "kernel", eintraege, "bpo" if bpo_da else "debian")
        if not bpo_ver and not bpo_da:
            self.text(v, "Die genaue Version steht erst fest, wenn die Paketliste geholt ist – das passiert "
                         "beim Anwenden von selbst%s." % ("" if backports_quelle()
                                                          else " (die Backports-Quelle wird dabei eingetragen)"),
                      klein=True)

        # --- Secure Boot ---
        v = self.gruppe("Secure Boot", "security-high")
        if sb is True and mok_offen():
            self.text(v, "<b>Der Schlüssel für die Zusatz-Treiber ist noch nicht bestätigt</b> – sie laufen "
                         "deshalb noch nicht. Den blauen Bildschirm beim Start verpasst? Hier gibt es einen "
                         "neuen Code.", ikon="data-warning")
            k = QPushButton(QIcon.fromTheme("dialog-password"), "Neuen Code für den blauen Bildschirm erstellen")
            k.setEnabled(not self.live)
            k.clicked.connect(lambda: self.starten(["mok=neu"]))
            v.addWidget(k)
        elif sb is True:
            self.text(v, "An. Zusatz-Treiber (Nvidia, Broadcom) müssen dafür einmal bestätigt werden: "
                         "Serafino zeigt dir dann einen Code, den du beim nächsten Start auf einem "
                         "blauen Bildschirm eingibst. Das ist normal und nur einmal nötig.")
        elif sb is False:
            self.text(v, "Aus. Zusatz-Treiber laufen ohne weiteren Schritt.")
        else:
            self.text(v, "Unbekannt (älterer Computer ohne UEFI?) – Zusatz-Treiber laufen ohne weiteren Schritt.")

        self.liste.addStretch(1)
        if self.live:
            self.status.setText("Im Live-Modus (vom Stick) lässt sich hier nur schauen. "
                                "Treiber installieren geht, wenn Serafino installiert ist.", "data-information")
        else:
            self.status.setText("Wähle aus und klicke auf „Änderungen anwenden“. Vorher wird eine "
                                "Sicherung angelegt.")

    def auswahl(self):
        """Nur echte Änderungen: {name: wert}"""
        out = {}
        for name, (g, werte, start) in self.wahl.items():
            w = werte.get(g.checkedId())
            if w is not None and w != start:
                out[name] = w
        return out

    def geaendert(self, *_):
        self.los.setEnabled(bool(self.auswahl()) and not self.live)

    # ---------- Anwenden ----------
    def anwenden(self):
        a = self.auswahl()
        if not a:
            return
        texte = {("nvidia", "an"): "Nvidia-Treiber installieren",
                 ("nvidia", "aus"): "Nvidia-Treiber entfernen (zurück zum freien Treiber)",
                 ("broadcom", "an"): "Broadcom-WLAN-Treiber installieren",
                 ("broadcom", "aus"): "Broadcom-WLAN-Treiber entfernen",
                 ("kernel", "bpo"): "Neueren Kernel aus Backports installieren",
                 ("kernel", "debian"): "Zurück zum Kernel von Debian 13"}
        liste = "\n".join("• " + texte[(k, w)] for k, w in a.items())
        box = QMessageBox(self)
        box.setWindowTitle("Hardware & Treiber")
        box.setIcon(QMessageBox.Icon.Question)
        box.setText("<b>Diese Änderungen anwenden?</b>")
        box.setInformativeText(liste + "\n\nVorher wird eine Sicherung angelegt. Das Ganze dauert einige "
                               "Minuten und braucht Internet. Danach ist ein Neustart nötig.")
        ok = box.addButton("Anwenden", QMessageBox.ButtonRole.AcceptRole)
        box.addButton("Abbrechen", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() is not ok:
            return
        self.starten(["nvidia=" + a.get("nvidia", "-"), "broadcom=" + a.get("broadcom", "-"),
                      "kernel=" + a.get("kernel", "-")])

    def starten(self, args):
        self.los.setEnabled(False)
        self.zu.setEnabled(False)
        for g, _, _ in self.wahl.values():
            for b in g.buttons():
                b.setEnabled(False)
        self.balken.show()
        self.status.setText("Ein Erwachsener muss gleich das Passwort eingeben …")
        self.mok_code, self.neustart, self.hinweise = None, False, []
        self.arbeiter = Arbeiter(args)
        self.arbeiter.zeile.connect(self.zeile)
        self.arbeiter.fertig.connect(self.fertig)
        self.arbeiter.start()

    def zeile(self, z):
        if z.startswith("SCHRITT: "):
            self.status.setText(z[9:])
        elif z.startswith("HINWEIS: "):
            self.hinweise.append(z[9:])
        elif z.startswith("MOK-CODE: "):
            self.mok_code = z[10:].strip()
        elif z.strip() == "NEUSTART":
            self.neustart = True

    def fertig(self, rc):
        self.balken.hide()
        self.zu.setEnabled(True)
        extra = ("\n\n" + "\n".join(self.hinweise)) if self.hinweise else ""
        if rc in (126, 127):
            self.status.setText("Abgebrochen – es wurde nichts geändert.")
            self.neu_laden()
            return
        if rc == 3:
            QMessageBox.information(self, "Hardware & Treiber", "Nichts installiert." + extra)
        elif rc != 0:
            QMessageBox.warning(self, "Hardware & Treiber",
                                "Das hat nicht geklappt." + extra + "\n\nDetails stehen in " + LOG +
                                ". Falls etwas nicht mehr läuft: Kontrollzentrum → Sicherung → "
                                "„Gestern wiederherstellen“.")
        if rc == 0 and self.mok_code:
            self.mok_anleitung()
        if rc == 0 and self.neustart:
            box = QMessageBox(self)
            box.setWindowTitle("Hardware & Treiber")
            box.setIcon(QMessageBox.Icon.Information)
            box.setText("<b>Fertig. Bitte den Computer neu starten.</b>")
            box.setInformativeText("Die Änderungen gelten nach dem Neustart." + extra)
            jetzt = box.addButton("Jetzt neu starten", QMessageBox.ButtonRole.AcceptRole)
            box.addButton("Später", QMessageBox.ButtonRole.RejectRole)
            box.exec()
            if box.clickedButton() is jetzt:
                subprocess.Popen(["pkexec", HELPER, "ts-reboot"])
        elif rc == 0:
            QMessageBox.information(self, "Hardware & Treiber", "Fertig." + extra)
        self.neu_laden()

    def mok_anleitung(self):
        box = QMessageBox(self)
        box.setWindowTitle("Secure Boot: einmal bestätigen")
        box.setIcon(QMessageBox.Icon.Information)
        box.setText("<b>Beim nächsten Start kommt ein blauer Bildschirm.</b><br><br>"
                    "Dein Code: <span style='font-size:22pt; font-family:monospace'><b>%s</b></span>"
                    % " ".join(self.mok_code[i:i + 4] for i in range(0, len(self.mok_code), 4)))
        box.setInformativeText(
            "Schreib dir den Code auf. Dann beim Neustart:\n\n"
            "1. „Enroll MOK“ wählen (Pfeiltasten, Enter)\n"
            "2. „Continue“ → „Yes“\n"
            "3. Den Code eingeben (ohne Leerzeichen) → Enter\n"
            "4. „Reboot“\n\n"
            "Der blaue Bildschirm wartet nur 10 Sekunden. Verpasst? Kein Problem: Der Treiber läuft dann "
            "noch nicht – hier unter „Secure Boot“ gibt es dann einen neuen Code.")
        box.exec()

    def neu_laden(self):
        self.close()
        neu = Fenster()
        neu.show()
        QApplication.instance()._fenster = neu


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("serafino-treiber")
    app.setDesktopFileName("serafino-treiber")
    w = Fenster()
    w.show()
    app._fenster = w
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
