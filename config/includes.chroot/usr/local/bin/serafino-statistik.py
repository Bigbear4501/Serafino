#!/usr/bin/env python3
"""serafino-statistik.py - Nutzung der Kinder (Eltern-Dashboard, bz2).

  serafino-statistik.py              Fenster für Eltern (Kontrollzentrum → „Nutzung“)
  serafino-statistik.py --erfassen   jede Minute als root (serafino-restzeit.service)

Erfasst pro Kinderkonto und Tag:
  • Bildschirmzeit (aus Timekpr, wie im Fenster „Bildschirmzeit“)
  • welche Programme wie viele Minuten geöffnet waren (nur Programme mit
    Eintrag im Startmenü, nur Name und Minuten – keine Fenstertitel,
    keine Webseiten, keine Inhalte)

Gespeichert nur auf diesem Computer in /var/lib/serafino/statistik/BENUTZER.json,
lesbar nur für Eltern (Gruppe sudo), nach 30 Tagen gelöscht. Nichts geht ins Internet.
"""
import configparser
import datetime
import glob
import json
import os
import pwd
import re
import subprocess
import sys

STATDIR = "/var/lib/serafino/statistik"
PROFDIR = "/var/lib/serafino/profiles"
ZEITDIR = "/run/serafino/restzeit"
APPDIRS = ["/usr/share/applications", "/usr/local/share/applications",
           "/var/lib/flatpak/exports/share/applications"]
TAGE_BEHALTEN = 30
# Programme, die nicht als „Programm des Kindes“ zählen (Oberfläche, Helfer)
NICHT_ZAEHLEN = re.compile(r"^(plasmashell|kded6|kwin.*|krunner|ksmserver|kactivitymanagerd|xdg-.*|"
                           r"systemsettings|org\.kde\.plasma.*|serafino-(?!youtube).*)$")
# Unsere Programme, die über ein Startskript laufen
EIGENE = {"serafino-youtube-kids-viewer.py": "YouTube Kids"}


# ------------------------------------------------------------------ Hilfen
def kinder():
    out = []
    for f in sorted(glob.glob(os.path.join(PROFDIR, "*"))):
        n = os.path.basename(f)
        try:
            pw = pwd.getpwnam(n)
        except KeyError:
            continue
        out.append((n, (pw.pw_gecos.split(",")[0] or n)))
    return out


def datei(user):
    return os.path.join(STATDIR, user + ".json")


def laden(user):
    try:
        with open(datei(user), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


# ------------------------------------------------------------------ Erfassen (root)
def programm_namen():
    """Programmdatei (oder Flatpak-ID) → Name aus dem Startmenü."""
    namen = {}
    for d in APPDIRS:
        for p in glob.glob(os.path.join(d, "*.desktop")):
            c = configparser.RawConfigParser(strict=False, interpolation=None)
            try:
                c.read(p, encoding="utf-8")
                e = c["Desktop Entry"]
            except (configparser.Error, KeyError, UnicodeDecodeError):
                continue
            if e.get("NoDisplay", "").lower() == "true" or e.get("Type", "Application") != "Application":
                continue
            name = e.get("Name[de]") or e.get("Name")
            if not name:
                continue
            stamm = os.path.basename(p)[:-8]
            if "/flatpak/" in p:
                namen["flatpak:" + stamm] = name
            teile = (e.get("Exec") or "").split()
            while teile and (teile[0] == "env" or "=" in teile[0]):
                teile = teile[1:]
            if teile:
                b = os.path.basename(teile[0])
                if b != "flatpak" and not NICHT_ZAEHLEN.match(b):
                    namen.setdefault(b, name)
    namen.update(EIGENE)
    return namen


def laufende_programme(uid, namen):
    gefunden = set()
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            if os.stat("/proc/" + pid).st_uid != uid:
                continue
            cmd = open("/proc/%s/cmdline" % pid, "rb").read().split(b"\0")
        except OSError:
            continue
        cmd = [c.decode("utf-8", "replace") for c in cmd if c]
        if not cmd:
            continue
        try:
            env = open("/proc/%s/environ" % pid, "rb").read()
            m = re.search(rb"(?:^|\0)FLATPAK_ID=([^\0]+)", env)
            if m and ("flatpak:" + m.group(1).decode()) in namen:
                gefunden.add(namen["flatpak:" + m.group(1).decode()])
                continue
        except OSError:
            pass
        b = os.path.basename(cmd[0])
        if re.match(r"^(python3?|perl|sh|bash)$", b) and len(cmd) > 1:
            b = os.path.basename(cmd[1])
        if b in namen and not NICHT_ZAEHLEN.match(b):
            gefunden.add(namen[b])
    return gefunden


def erfassen():
    os.makedirs(STATDIR, exist_ok=True)
    try:
        os.chown(STATDIR, 0, _gruppe("sudo"))
        os.chmod(STATDIR, 0o750)
    except OSError:
        pass
    heute = datetime.date.today().isoformat()
    grenze = (datetime.date.today() - datetime.timedelta(days=TAGE_BEHALTEN)).isoformat()
    namen = None
    for user, _ in kinder():
        uid = pwd.getpwnam(user).pw_uid
        d = laden(user)
        tage = {k: v for k, v in d.get("tage", {}).items() if k > grenze}
        t = tage.setdefault(heute, {"zeit": 0, "apps": {}})
        try:                                   # Bildschirmzeit von Timekpr (serafino-restzeit.sh)
            genutzt = int(open(os.path.join(ZEITDIR, user)).read().split()[1])
            t["zeit"] = max(t.get("zeit", 0), genutzt)
        except (OSError, ValueError, IndexError):
            pass
        angemeldet = subprocess.run(["loginctl", "show-user", user, "-p", "State", "--value"],
                                    capture_output=True, text=True).stdout.strip() in ("active", "online")
        if angemeldet:
            if namen is None:
                namen = programm_namen()
            for prog in laufende_programme(uid, namen):
                t["apps"][prog] = t["apps"].get(prog, 0) + 1
        d["tage"] = tage
        tmp = datei(user) + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False)
        os.chmod(tmp, 0o640)
        try:
            os.chown(tmp, 0, _gruppe("sudo"))
        except OSError:
            pass
        os.replace(tmp, datei(user))
    return 0


def _gruppe(name):
    import grp
    try:
        return grp.getgrnam(name).gr_gid
    except KeyError:
        return 0


# ------------------------------------------------------------------ Fenster (Eltern)
def fenster():
    from PyQt6.QtCore import Qt, QRectF
    from PyQt6.QtGui import QIcon, QPainter, QColor, QFont, QPen
    from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                 QLabel, QComboBox, QFrame, QSizePolicy, QScrollArea)

    GRUEN, TEXT, LEISE, SPUR = "#2e8a57", "#1d2329", "#56636f", "#e4eef4"

    def zeit_text(sek):
        m = int(round(sek / 60))
        if m < 60:
            return "%d Min." % m
        return "%d Std. %02d Min." % (m // 60, m % 60)

    class Balken(QWidget):
        """Säulen: Bildschirmzeit der letzten 14 Tage."""
        def __init__(self):
            super().__init__()
            self.werte = []
            self.setMinimumHeight(190)
            self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        def setze(self, werte):
            self.werte = werte
            self.update()

        def paintEvent(self, _e):
            p = QPainter(self)
            p.setRenderHint(QPainter.RenderHint.Antialiasing)
            pal = self.palette()
            text = pal.color(pal.ColorRole.WindowText)
            leise = QColor(text); leise.setAlpha(150)
            if not self.werte:
                return
            h_text = 34
            hoch = self.height() - h_text - 18
            mx = max([w for _, w in self.werte] + [60 * 60])
            n = len(self.werte)
            breit = self.width() / n
            f = QFont(self.font()); f.setPixelSize(11); p.setFont(f)
            for i, (tag, sek) in enumerate(self.werte):
                x = i * breit + breit * 0.18
                b = breit * 0.64
                h = max(3, hoch * sek / mx) if sek else 0
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QColor(SPUR) if not self.palette().color(pal.ColorRole.Window).lightness() < 128
                           else QColor("#1c3245"))
                p.drawRoundedRect(QRectF(x, 18, b, hoch), 4, 4)
                p.setBrush(QColor(GRUEN))
                if h:
                    p.drawRoundedRect(QRectF(x, 18 + hoch - h, b, h), 4, 4)
                p.setPen(QPen(leise))
                p.drawText(QRectF(i * breit, self.height() - h_text + 2, breit, 16),
                           Qt.AlignmentFlag.AlignCenter, ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"][tag.weekday()])
                p.drawText(QRectF(i * breit, self.height() - h_text + 17, breit, 16),
                           Qt.AlignmentFlag.AlignCenter, "%d." % tag.day)
                if sek:
                    p.setPen(QPen(text))
                    p.drawText(QRectF(i * breit, 18 + hoch - h - 16, breit, 14),
                               Qt.AlignmentFlag.AlignCenter, str(int(round(sek / 60))))
            p.end()

    class Karte(QFrame):
        def __init__(self, titel):
            super().__init__()
            self.setFrameShape(QFrame.Shape.StyledPanel)
            v = QVBoxLayout(self)
            t = QLabel(titel); t.setStyleSheet("color:palette(placeholder-text)")
            self.wert = QLabel("–")
            f = self.wert.font(); f.setPointSizeF(f.pointSizeF() * 1.6); f.setBold(True); self.wert.setFont(f)
            v.addWidget(t); v.addWidget(self.wert)

    class ProgrammZeile(QWidget):
        def __init__(self, name, minuten, mx):
            super().__init__()
            h = QHBoxLayout(self); h.setContentsMargins(0, 2, 0, 2)
            n = QLabel(name); n.setMinimumWidth(190)
            h.addWidget(n)
            bar = QFrame(); bar.setFixedHeight(12)
            bar.setStyleSheet("background:%s;border-radius:6px" % GRUEN)
            bar.setFixedWidth(max(6, int(320 * minuten / max(mx, 1))))
            h.addWidget(bar)
            z = QLabel(zeit_text(minuten * 60)); z.setStyleSheet("color:palette(placeholder-text)")
            h.addWidget(z)
            h.addStretch(1)

    class Fenster(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Nutzung der Kinder")
            self.setWindowIcon(QIcon.fromTheme("office-chart-bar"))
            self.resize(820, 660)
            w = QWidget(); self.setCentralWidget(w)
            v = QVBoxLayout(w); v.setContentsMargins(20, 16, 20, 14)

            kopf = QHBoxLayout()
            ik = QLabel(); ik.setPixmap(QIcon.fromTheme("office-chart-bar").pixmap(32, 32))
            kopf.addWidget(ik)
            t = QLabel("Nutzung der Kinder")
            f = t.font(); f.setPointSizeF(f.pointSizeF() * 1.35); f.setBold(True); t.setFont(f)
            kopf.addWidget(t, 1)
            self.wahl = QComboBox()
            for user, name in kinder():
                self.wahl.addItem(QIcon.fromTheme("im-user"), "%s (%s)" % (name, user) if name != user else user, user)
            self.wahl.currentIndexChanged.connect(self.zeigen)
            kopf.addWidget(self.wahl)
            v.addLayout(kopf)

            karten = QHBoxLayout()
            self.k_heute, self.k_gestern, self.k_schnitt = Karte("Heute"), Karte("Gestern"), Karte("Pro Tag (letzte Woche)")
            for k in (self.k_heute, self.k_gestern, self.k_schnitt):
                karten.addWidget(k)
            v.addLayout(karten)

            u1 = QLabel("<b>Bildschirmzeit der letzten 14 Tage</b> (Minuten)")
            v.addSpacing(8); v.addWidget(u1)
            self.balken = Balken(); v.addWidget(self.balken)

            u2 = QLabel("<b>Programme der letzten 7 Tage</b> – wie lange sie geöffnet waren")
            v.addSpacing(8); v.addWidget(u2)
            self.liste_w = QWidget(); self.liste = QVBoxLayout(self.liste_w); self.liste.setContentsMargins(0, 0, 0, 0)
            sc = QScrollArea(); sc.setWidgetResizable(True); sc.setFrameShape(QFrame.Shape.NoFrame)
            sc.setWidget(self.liste_w)
            v.addWidget(sc, 1)

            hin = QHBoxLayout()
            hik = QLabel(); hik.setPixmap(QIcon.fromTheme("security-high").pixmap(16, 16))
            hin.addWidget(hik, 0, Qt.AlignmentFlag.AlignTop)
            hint = QLabel("Bleibt auf diesem Computer: gespeichert werden nur Bildschirmzeit, Programmname und "
                          "Minuten – keine Webseiten, keine Inhalte. Nach 30 Tagen wird alles gelöscht. "
                          "Nichts geht ins Internet.")
            hint.setWordWrap(True); hint.setStyleSheet("color:palette(placeholder-text)")
            hin.addWidget(hint, 1)
            v.addLayout(hin)

            if self.wahl.count() == 0:
                self.liste.addWidget(QLabel("Es gibt noch keine Kinderkonten."))
            else:
                self.zeigen()

        def zeigen(self):
            while self.liste.count():
                it = self.liste.takeAt(0)
                if it.widget():
                    it.widget().deleteLater()
            user = self.wahl.currentData()
            if not user:
                return
            if not os.access(datei(user), os.R_OK) and os.path.exists(datei(user)):
                self.liste.addWidget(QLabel("Nur Eltern-Konten können die Nutzung sehen."))
                return
            tage = laden(user).get("tage", {})
            heute = datetime.date.today()
            def zeit(tag):
                return tage.get(tag.isoformat(), {}).get("zeit", 0)
            self.k_heute.wert.setText(zeit_text(zeit(heute)))
            self.k_gestern.wert.setText(zeit_text(zeit(heute - datetime.timedelta(days=1))))
            woche = [zeit(heute - datetime.timedelta(days=i)) for i in range(1, 8)]
            self.k_schnitt.wert.setText(zeit_text(sum(woche) / 7) if any(woche) else "–")
            self.balken.setze([(heute - datetime.timedelta(days=i), zeit(heute - datetime.timedelta(days=i)))
                               for i in range(13, -1, -1)])
            summe = {}
            for i in range(7):
                for prog, m in tage.get((heute - datetime.timedelta(days=i)).isoformat(), {}).get("apps", {}).items():
                    summe[prog] = summe.get(prog, 0) + m
            if not summe:
                lb = QLabel("Noch keine Programme erfasst. Die Übersicht füllt sich, sobald das Kind "
                            "angemeldet ist und etwas startet.")
                lb.setWordWrap(True)
                self.liste.addWidget(lb)
            else:
                mx = max(summe.values())
                for prog, m in sorted(summe.items(), key=lambda x: -x[1])[:12]:
                    self.liste.addWidget(ProgrammZeile(prog, m, mx))
            self.liste.addStretch(1)

    app = QApplication(sys.argv)
    import serafino_deutsch; serafino_deutsch.an(app)
    app.setDesktopFileName("serafino-statistik")
    w = Fenster(); w.show()
    return app.exec()


if __name__ == "__main__":
    if "--erfassen" in sys.argv:
        if os.geteuid() != 0:
            sys.exit("Nur als root (läuft von selbst jede Minute).")
        sys.exit(erfassen())
    sys.exit(fenster())
