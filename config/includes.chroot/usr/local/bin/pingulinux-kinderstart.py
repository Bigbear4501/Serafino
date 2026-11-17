#!/usr/bin/env python3
"""pingulinux-kinderstart.py - einfacher Startbildschirm für Kinder von 2 bis 6 (be4).

Ganzer Bildschirm mit wenigen großen Bild-Kacheln, Fino oben, Restzeit als
Sonne, die langsam untergeht. Beim Antippen sagt eine Stimme den Namen.
Kacheln können Gruppen sein (z. B. „Spielen“ → zweite Seite mit „Zurück“).

Aufruf:
  pingulinux-kinderstart.py              Startbildschirm zeigen
  pingulinux-kinderstart.py --auto       beim Anmelden (Autostart): nur, wenn
                                         das Konto die einfache Oberfläche hat
  pingulinux-kinderstart.py --bearbeiten BENUTZER
                                         Kacheln eines Kindes einrichten (Eltern)

Einstellungen pro Kind: /var/lib/pingulinux/kinderstart/BENUTZER.json
(nur root darf schreiben – gespeichert wird über
pkexec pingulinux-root-helper ks-save BENUTZER, also mit Eltern-Passwort).
  {"modus": "auto"|"an"|"aus",          auto = bis 6 Jahre
   "max_lautstaerke": 100,                wird nicht mehr benutzt (Obergrenze entfernt, 17. Nov)
   "kacheln": [ {"app": "tuxpaint.desktop", "name": "Malen"},
                {"gruppe": "Spielen", "symbol": "🧩",
                 "kacheln": [ {"app": "org.kde.ktuberling.desktop"} ]} ]}
Ohne Datei gilt eine Vorgabe nach Alter.

Es gibt keinen Weg in den normalen Bereich der Eltern (Wunsch Mike, 17. Nov, be4m):
unten rechts nur zwei Knöpfe, „Herunterfahren“ und „Abmelden“ (ohne Passwort).
Eltern melden sich zum Wechseln ab und mit ihrem Konto an. Jedes Programm lässt
sich nur einmal öffnen (zweites Antippen holt das laufende nach vorn). Jede Kachel hat oben rechts einen
Vorlese-Knopf 🗣️, der nur den Namen vorliest. Oben gibt es große Knöpfe
„leiser“/„lauter“ mit Balken (bis 100 %). Eine Obergrenze gibt es nicht mehr
(Wunsch Mike, 17. Nov – am Surface war der Ton damit zu leise).
Kinder können nichts hinzufügen oder löschen: Kacheln richten die Eltern im
Kontrollzentrum ein („Startbildschirm der Kleinen“, Speichern mit Passwort).
"""
import configparser
import glob
import json
import os
import pwd
import re
import shlex
import signal
import subprocess
import sys

from PyQt6.QtCore import Qt, QTimer, QSize, QRectF, QPointF
from PyQt6.QtGui import (QIcon, QPixmap, QPainter, QFont, QColor, QLinearGradient,
                         QPainterPath, QBrush, QPen)
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QPushButton, QToolButton, QScrollArea, QSizePolicy,
                             QDialog, QListWidget, QListWidgetItem, QTreeWidget,
                             QTreeWidgetItem, QComboBox, QInputDialog, QMessageBox,
                             QAbstractItemView, QStackedWidget)

LOGO = "/usr/share/pingulinux/fino/fino.png"
PROFDIR = "/var/lib/pingulinux/profiles"
CONFDIR = "/var/lib/pingulinux/kinderstart"
ZEITDIR = "/run/pingulinux/restzeit"
HELPER = ["pkexec", "/usr/local/bin/pingulinux-root-helper"]
APPDIRS = ["/usr/share/applications", "/var/lib/flatpak/exports/share/applications",
           "/usr/local/share/applications"]
AUTO_BIS = 6
FARBEN = ["#ffe1e8", "#fff1c9", "#dff3d4", "#dcecff", "#ffd9d2", "#eadcff"]
GRUPPEN_SYMBOLE = ["🧩", "🎨", "📚", "🎵", "⭐", "🐾", "🚀", "🌈", "🎲", "🔤"]

# Vorgabe, wenn die Eltern noch nichts eingerichtet haben (gefiltert nach Alter
# und danach, was installiert ist). Mehrere Namen = verschiedene Paketversionen.
VORGABE = [
    (["tuxpaint.desktop"], "Malen"),
    (["org.kde.gcompris.desktop", "gcompris-qt.desktop"], "Spielen & Lernen"),
    (["org.kde.ktuberling.desktop", "ktuberling.desktop"], "Gesichter basteln"),
    (["org.kde.klettres.desktop", "klettres.desktop"], "Buchstaben"),
    (["pingulinux-youtube-kids.desktop"], "Filme"),
    (["tuxtype.desktop"], "Tippen"),
    (["tuxmath.desktop"], "Rechnen"),
]


# ---------------------------------------------------------------- Daten
def alter(user):
    try:
        return int(open(os.path.join(PROFDIR, user)).read().strip())
    except (OSError, ValueError):
        return None


def vorname(user):
    try:
        g = pwd.getpwnam(user).pw_gecos.split(",")[0].strip()
        return (g or user).split()[0]
    except KeyError:
        return user


def lade_conf(user):
    try:
        with open(os.path.join(CONFDIR, user + ".json"), encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict):
            return d
    except (OSError, ValueError):
        pass
    return {}


def aktiv_fuer(user):
    """Soll dieses Konto die einfache Oberfläche bekommen?"""
    a = alter(user)
    if a is None:                      # kein Kinderkonto
        return False
    modus = lade_conf(user).get("modus", "auto")
    if modus == "an":
        return True
    if modus == "aus":
        return False
    return a <= AUTO_BIS


def finde_desktop(name):
    for d in APPDIRS:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            return p
    return None


def lies_desktop(path):
    cp = configparser.ConfigParser(interpolation=None, strict=False)
    cp.optionxform = str
    try:
        cp.read(path, encoding="utf-8")
        return dict(cp["Desktop Entry"])
    except (configparser.Error, KeyError, OSError):
        return {}


def gesperrt(user, desktop_name):
    """Altersregeln blenden Programme pro Konto aus
    (~/.local/share/applications/NAME mit X-Pingulinux-Hidden / NoDisplay)."""
    try:
        home = pwd.getpwnam(user).pw_dir
    except KeyError:
        return False
    p = os.path.join(home, ".local/share/applications", desktop_name)
    try:
        t = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    return "X-Pingulinux-Hidden=true" in t or re.search(r"^(NoDisplay|Hidden)=true", t, re.M) is not None


def app_info(desktop_name):
    path = finde_desktop(desktop_name)
    if not path:
        return None
    e = lies_desktop(path)
    name = e.get("Name[de]") or e.get("Name") or desktop_name
    return {"path": path, "name": name, "icon": e.get("Icon", ""), "exec": e.get("Exec", "")}


def erlaubte_apps(user):
    """Alle Programme mit Menü-Eintrag, die für dieses Kind freigegeben sind."""
    out = {}
    for d in APPDIRS:
        for p in glob.glob(os.path.join(d, "*.desktop")):
            n = os.path.basename(p)
            if n in out:
                continue
            e = lies_desktop(p)
            if not e or e.get("Type") != "Application" or e.get("NoDisplay") == "true":
                continue
            if n.startswith("pingulinux-") and n != "pingulinux-youtube-kids.desktop":
                continue                      # Eltern-Werkzeuge nicht anbieten
            if gesperrt(user, n):
                continue
            out[n] = e.get("Name[de]") or e.get("Name") or n
    return dict(sorted(out.items(), key=lambda kv: kv[1].lower()))


def vorgabe_kacheln(user):
    erlaubt = erlaubte_apps(user)
    k = []
    for namen, titel in VORGABE:
        for n in namen:
            if n in erlaubt:
                k.append({"app": n, "name": titel})
                break
    return k


def kacheln_fuer(user):
    conf = lade_conf(user)
    k = conf.get("kacheln")
    if isinstance(k, list) and k:
        return k
    return vorgabe_kacheln(user)


def restzeit(user):
    """(übrig_sek, genutzt_sek) aus /run/pingulinux/restzeit/BENUTZER oder None."""
    try:
        a, b = open(os.path.join(ZEITDIR, user)).read().split()[:2]
        return int(a), int(b)
    except (OSError, ValueError):
        return None


def _hauptprogramm(teile):
    """Der eigentliche Programmname hinter „env VAR=x“ usw. (für die Einmal-Prüfung)."""
    t = list(teile)
    while t and (os.path.basename(t[0]) == "env" or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", t[0])
                 or t[0].startswith("-")):
        t.pop(0)
    return t


def laeuft_schon(teile):
    """Läuft dieses Programm im eigenen Konto schon? (be4m: jedes nur einmal)"""
    t = _hauptprogramm(teile)
    if not t:
        return False
    name = os.path.basename(t[0])
    schluessel = None
    if name == "flatpak":                         # flatpak run [Optionen] APP-ID
        rest = [x for x in t[1:] if x != "run" and not x.startswith("-")]
        schluessel = rest[0] if rest else None
    uid, eigen = os.getuid(), os.getpid()
    skripte = ("python", "sh", "bash", "perl", "ruby", "node")
    for d in glob.glob("/proc/[0-9]*"):
        try:
            if int(os.path.basename(d)) == eigen or os.stat(d).st_uid != uid:
                continue
            arg = open(d + "/cmdline", "rb").read().split(b"\0")
            arg = [a.decode("utf-8", "replace") for a in arg if a]
        except (OSError, ValueError):
            continue
        if not arg:
            continue
        if schluessel:
            if schluessel in arg:
                return True
            continue
        if os.path.basename(arg[0]) == name:
            return True
        if len(arg) > 1 and os.path.basename(arg[0]).startswith(skripte) \
                and os.path.basename(arg[1]) == name:
            return True
    return False


def starte(desktop_name):
    """Programm aus seinem Menü-Eintrag starten (ohne %f/%u-Platzhalter).
    Läuft es schon, wird nichts Neues gestartet: Rückgabe "laeuft"."""
    info = app_info(desktop_name)
    if not info or not info["exec"]:
        return False
    try:
        teile = [t for t in shlex.split(info["exec"]) if not re.fullmatch(r"%[a-zA-Z]", t)]
    except ValueError:
        return False
    if laeuft_schon(teile):
        return "laeuft"
    try:
        return subprocess.Popen(teile, start_new_session=True,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError:
        return None


def sprich(text):
    """Namen vorlesen (espeak-ng, deutsch). Fehlt es, passiert einfach nichts."""
    for cmd in (["espeak-ng", "-v", "de", "-s", "140", text], ["spd-say", "-l", "de", text]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue


def emoji_icon(emoji, size=128):
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    f = QFont()
    f.setPixelSize(int(size * 0.8))
    p.setFont(f)
    p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, emoji)
    p.end()
    return QIcon(pm)


def icon_fuer(icon_name):
    if not icon_name:
        return QIcon()
    if os.path.isabs(icon_name) and os.path.exists(icon_name):
        return QIcon(icon_name)
    return QIcon.fromTheme(icon_name)


# ---------------------------------------------------------------- Lautstärke
LAUT_VORGABE = 70
LAUT_SCHRITT = 10
PIEP = ["/usr/share/sounds/ocean/stereo/audio-volume-change.oga",
        "/usr/share/sounds/freedesktop/stereo/audio-volume-change.oga"]


def _aus(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=3).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def max_lautstaerke(user):
    """Keine Obergrenze mehr (17. Nov): der Balken reicht immer bis 100 %."""
    return 100


def lautstaerke():
    """Aktuelle Lautstärke in % (PipeWire/wpctl, sonst pactl), None wenn unbekannt."""
    m = re.search(r"Volume:\s*([0-9.]+)", _aus(["wpctl", "get-volume", "@DEFAULT_AUDIO_SINK@"]))
    if m:
        return int(round(float(m.group(1)) * 100))
    m = re.search(r"(\d+)%", _aus(["pactl", "get-sink-volume", "@DEFAULT_SINK@"]))
    return int(m.group(1)) if m else None


def setze_lautstaerke(prozent):
    prozent = max(0, min(100, int(prozent)))
    if _aus(["wpctl", "status"]):
        _aus(["wpctl", "set-volume", "@DEFAULT_AUDIO_SINK@", "%.2f" % (prozent / 100)])
        _aus(["wpctl", "set-mute", "@DEFAULT_AUDIO_SINK@", "0"])
    else:
        _aus(["pactl", "set-sink-volume", "@DEFAULT_SINK@", "%d%%" % prozent])
        _aus(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])


def piep():
    """Kurzer Ton, damit das Kind hört, wie laut es jetzt ist."""
    for f in PIEP:
        if os.path.exists(f):
            for cmd in (["pw-play", f], ["paplay", f]):
                try:
                    subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return
                except OSError:
                    continue


class LautBalken(QWidget):
    """Sieben Balken, die nach rechts höher werden – voll = Obergrenze der Eltern."""

    def __init__(self):
        super().__init__()
        self.anteil = 0.0
        self.setFixedSize(150, 56)

    def setze(self, anteil):
        self.anteil = max(0.0, min(1.0, anteil))
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        n, gap = 7, 6
        bw = (self.width() - gap * (n - 1)) / n
        voll = round(self.anteil * n)
        for i in range(n):
            h = self.height() * (0.3 + 0.7 * (i + 1) / n)
            r = QRectF(i * (bw + gap), self.height() - h, bw, h)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(QColor("#2e8a57") if i < voll else QColor(31, 53, 87, 45))
            p.drawRoundedRect(r, 5, 5)
        p.end()


# ---------------------------------------------------------------- Sonne
class Sonne(QWidget):
    """Restzeit als Bild: Die Sonne geht im Lauf der erlaubten Zeit unter."""

    def __init__(self):
        super().__init__()
        self.anteil = 1.0
        self.setFixedSize(190, 72)

    def setze(self, anteil):
        self.anteil = max(0.0, min(1.0, anteil))
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(0, 0, self.width(), self.height())
        path = QPainterPath()
        path.addRoundedRect(r, 16, 16)
        p.setClipPath(path)
        g = QLinearGradient(0, 0, 0, self.height())
        if self.anteil > 0.25:
            g.setColorAt(0, QColor("#ffd56b")); g.setColorAt(1, QColor("#ffecb8"))
        else:                                   # Abendhimmel
            g.setColorAt(0, QColor("#ff9a6b")); g.setColorAt(1, QColor("#ffc9a8"))
        p.fillRect(r, QBrush(g))
        # Sonne: oben bei 100 %, hinter dem Hügel bei 0 %
        y = 6 + (1 - self.anteil) * 46         # bei 0 % ganz hinter dem Hügel, vorher noch sichtbar
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor("#ff9f1a"))
        p.drawEllipse(QPointF(self.width() * 0.62, y + 20), 22, 22)
        p.setBrush(QColor("#7cc463"))
        p.drawEllipse(QRectF(-20, self.height() - 22, self.width() + 40, 60))
        p.end()


# ---------------------------------------------------------------- Kachel
# ---------------------------------------------------------------- Nach Hause (be4h)
# Ein runder Knopf mit Haus, immer unten links über jedem Programm, das vom
# Startbildschirm aus gestartet wurde. Antippen beendet diese Programme und
# zeigt wieder den Startbildschirm. Damit der Knopf auch über Spielen und
# Videos bleibt, setzt der Startbildschirm für dieses Konto KWin-Regeln:
# Knopf immer oben, ohne Rahmen, nicht in der Taskleiste; kein echtes Vollbild
# für andere Fenster (sonst würde es den Knopf verdecken).
KNOPF_TITEL = "Nach Hause"
KNOPF_GROESSE = 104
KWINRULES = os.path.expanduser("~/.config/kwinrulesrc")
REGEL_IDS = ["pingulinux-nachhause", "pingulinux-startbildschirm", "pingulinux-kein-vollbild"]


def _kwin_lesen():
    c = configparser.RawConfigParser(strict=False, interpolation=None)
    c.optionxform = str
    try:
        c.read(KWINRULES, encoding="utf-8")
    except (configparser.Error, OSError):
        return None
    return c


def _kwin_schreiben(c):
    os.makedirs(os.path.dirname(KWINRULES), exist_ok=True)
    with open(KWINRULES, "w", encoding="utf-8") as f:
        c.write(f, space_around_delimiters=False)
    try:
        subprocess.run(["dbus-send", "--session", "--type=method_call", "--dest=org.kde.KWin",
                        "/KWin", "org.kde.KWin.reconfigure"], timeout=5,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass


def kwin_regeln(an, x=24, y=600):
    """Regeln für den Nach-Hause-Knopf setzen (an=True) oder entfernen."""
    c = _kwin_lesen()
    if c is None:
        return
    if not c.has_section("General"):
        c.add_section("General")
    andere = [r for r in c.get("General", "rules", fallback="").split(",") if r and r not in REGEL_IDS]
    for r in REGEL_IDS:
        if c.has_section(r):
            c.remove_section(r)
    if an:
        klasse = {"wmclass": "pingulinux-kinderstart", "wmclassmatch": "1", "wmclasscomplete": "false"}
        regeln = {
            "pingulinux-nachhause": dict(klasse, Description="Serafino: Nach-Hause-Knopf",
                                         title=KNOPF_TITEL, titlematch="1",
                                         above="true", aboverule="2", noborder="true", noborderrule="2",
                                         skiptaskbar="true", skiptaskbarrule="2",
                                         skippager="true", skippagerrule="2",
                                         skipswitcher="true", skipswitcherrule="2",
                                         position="%d,%d" % (x, y), positionrule="2",
                                         minimize="false", minimizerule="2"),
            "pingulinux-startbildschirm": dict(klasse, Description="Serafino: Startbildschirm der Kleinen",
                                               title="Mein Startbildschirm", titlematch="1",
                                               fullscreen="true", fullscreenrule="2"),
            "pingulinux-kein-vollbild": {"Description": "Serafino: kein Vollbild (Nach-Hause-Knopf bleibt sichtbar)",
                                         "wmclassmatch": "0", "fullscreen": "false", "fullscreenrule": "2"},
        }
        for r in REGEL_IDS:            # Reihenfolge zählt: der Startbildschirm vor „kein Vollbild“
            c.add_section(r)
            for k, v in regeln[r].items():
                c.set(r, k, v)
        alle = REGEL_IDS + andere
    else:
        alle = andere
        if not alle and len(c.sections()) == 1:
            try:
                os.remove(KWINRULES)
            except OSError:
                return
            _kwin_schreiben_nur_neu_laden()
            return
    c.set("General", "count", str(len(alle)))
    c.set("General", "rules", ",".join(alle))
    _kwin_schreiben(c)


def _kwin_schreiben_nur_neu_laden():
    try:
        subprocess.run(["dbus-send", "--session", "--type=method_call", "--dest=org.kde.KWin",
                        "/KWin", "org.kde.KWin.reconfigure"], timeout=5,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        pass


def kwin_regeln_da():
    c = _kwin_lesen()
    return bool(c and c.has_section(REGEL_IDS[0]))


class NachHause(QWidget):
    """Runder Knopf mit Haus. Eigenes, kleines Fenster ohne Rahmen."""

    def __init__(self, beim_tippen):
        super().__init__(None, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
                         | Qt.WindowType.Tool)
        self.setWindowTitle(KNOPF_TITEL)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(KNOPF_GROESSE, KNOPF_GROESSE)
        self.setToolTip("Nach Hause – zurück zu meinem Startbildschirm")
        self.setAccessibleName("Nach Hause")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.beim_tippen = beim_tippen
        self.gedrueckt = False

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(6, 6, KNOPF_GROESSE - 12, KNOPF_GROESSE - 12)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(0, 0, 0, 45))                    # Schatten
        p.drawEllipse(r.translated(0, 4))
        p.setBrush(QColor("#ffe9a8") if self.gedrueckt else QColor("#ffffff"))
        p.setPen(QPen(QColor("#f2a51f"), 5))
        p.drawEllipse(r)
        f = QFont(); f.setPixelSize(int(KNOPF_GROESSE * 0.48)); p.setFont(f)
        p.drawText(r, Qt.AlignmentFlag.AlignCenter, "🏠")
        p.end()

    def mousePressEvent(self, e):
        self.gedrueckt = True; self.update()

    def mouseReleaseEvent(self, e):
        self.gedrueckt = False; self.update()
        if self.rect().contains(e.position().toPoint()):
            self.beim_tippen()


class Kachel(QToolButton):
    """Große Kachel. Antippen startet (und sagt den Namen). Oben rechts ein
    deutlicher Lautsprecher-Knopf: der liest NUR den Namen vor, startet nichts –
    zum Ausprobieren für Kinder, die noch nicht lesen. Symbol: sprechender Kopf 🗣️,
    damit er nicht mit „lauter“ 🔊 oben verwechselt wird."""

    def __init__(self, titel, icon, farbe, gestrichelt=False, klein="", vorlesen=None):
        super().__init__()
        anzeige = titel
        if len(titel) > 15 and " " in titel and not klein:    # lange Namen in zwei Zeilen statt „Gesich…asteln“
            mitte = len(titel) // 2
            pos = min((i for i, c in enumerate(titel) if c == " "), key=lambda i: abs(i - mitte))
            anzeige = titel[:pos] + "\n" + titel[pos + 1:]
        self.setText(anzeige.replace("&", "&&") + ("\n" + klein if klein else ""))
        self.setIcon(icon)
        self.setIconSize(QSize(120, 120))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(200, 180)
        self.setMaximumHeight(300)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        f = self.font(); f.setPixelSize(30); f.setBold(True); self.setFont(f)
        rand = "4px dashed rgba(31,53,87,.4)" if gestrichelt else "none"
        self.setStyleSheet(
            "Kachel{background:%s;border:%s;border-radius:36px;color:#1f3557;"
            "padding:14px;border-bottom:8px solid rgba(0,0,0,.12)}"
            "Kachel:pressed{padding-top:20px;border-bottom:2px solid rgba(0,0,0,.12)}"
            % (farbe, rand))
        self.laut = None
        if vorlesen:
            self.laut = QToolButton(self)
            self.laut.setText("🗣️")          # sprechender Kopf = vorlesen (🔊 ist oben „lauter“)
            self.laut.setToolTip("Vorlesen: „%s“" % vorlesen)
            self.laut.setAccessibleName("%s vorlesen" % vorlesen)
            self.laut.setFixedSize(66, 66)
            self.laut.setCursor(Qt.CursorShape.PointingHandCursor)
            lf = self.laut.font(); lf.setPixelSize(36); self.laut.setFont(lf)
            self.laut.setStyleSheet("QToolButton{background:#ffffff;border:3px solid #9fb3c8;"
                                    "border-radius:33px;padding:0}"
                                    "QToolButton:pressed{background:#ffe9a8;border-color:#f2a51f}")
            self.laut.clicked.connect(lambda _=False, t=vorlesen: sprich(t))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if self.laut:
            self.laut.move(self.width() - self.laut.width() - 14, 14)


# ---------------------------------------------------------------- Startbildschirm
class Startbildschirm(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Mein Startbildschirm")
        if os.path.exists(LOGO):
            self.setWindowIcon(QIcon(LOGO))
        self.setStyleSheet("Startbildschirm{background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
                           "stop:0 #bfe3ff, stop:0.55 #e8f6ff, stop:0.551 #bfe8a8, stop:1 #8fd16f)}")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        v = QVBoxLayout(self)
        v.setContentsMargins(36, 20, 36, 16)
        oben = QHBoxLayout()
        if os.path.exists(LOGO):
            logo = QLabel(); logo.setPixmap(QIcon(LOGO).pixmap(92, 92)); oben.addWidget(logo)
        self.titel = QLabel()
        f = self.titel.font(); f.setPixelSize(46); f.setBold(True); self.titel.setFont(f)
        self.titel.setStyleSheet("color:#1f3557")
        oben.addWidget(self.titel)
        oben.addStretch(1)
        # Lautstärke: leiser / Balken / lauter
        self.lautmax = max_lautstaerke(self.user)
        self.lautbox = QWidget()
        self.lautbox.setStyleSheet("background:rgba(255,255,255,.6);border-radius:26px")
        lb = QHBoxLayout(self.lautbox); lb.setContentsMargins(10, 8, 10, 8); lb.setSpacing(10)
        self.leiser = QPushButton("🔉"); self.lauter = QPushButton("🔊")
        for k, tip in ((self.leiser, "Leiser"), (self.lauter, "Lauter")):
            k.setFixedSize(66, 66)
            k.setToolTip(tip); k.setAccessibleName(tip)
            k.setCursor(Qt.CursorShape.PointingHandCursor)
            kf = k.font(); kf.setPixelSize(34); k.setFont(kf)
            k.setStyleSheet("QPushButton{background:#ffffff;border:3px solid #9fb3c8;border-radius:33px;padding:0}"
                            "QPushButton:pressed{background:#ffe9a8;border-color:#f2a51f}")
        self.balken = LautBalken()
        self.balken.setStyleSheet("background:transparent")
        lb.addWidget(self.leiser); lb.addWidget(self.balken); lb.addWidget(self.lauter)
        self.leiser.clicked.connect(lambda: self.laut_aendern(-LAUT_SCHRITT))
        self.lauter.clicked.connect(lambda: self.laut_aendern(+LAUT_SCHRITT))
        oben.addWidget(self.lautbox)
        oben.addSpacing(16)
        self.sonnebox = QWidget()
        self.sonnebox.setStyleSheet("background:rgba(255,255,255,.6);border-radius:26px")
        sb = QHBoxLayout(self.sonnebox); sb.setContentsMargins(14, 10, 22, 10)
        self.sonne = Sonne(); sb.addWidget(self.sonne)
        self.zeittext = QLabel(); self.zeittext.setStyleSheet("background:transparent;color:#1f3557")
        f = self.zeittext.font(); f.setPixelSize(22); f.setBold(True); self.zeittext.setFont(f)
        sb.addWidget(self.zeittext)
        # „Mehr Zeit bitte“ (be15): Fino fragt, Mama oder Papa geben mit Passwort frei
        self.mehrzeit = QPushButton("🙋 Mehr Zeit")
        f = self.mehrzeit.font(); f.setPixelSize(20); f.setBold(True); self.mehrzeit.setFont(f)
        self.mehrzeit.setStyleSheet("QPushButton{background:#f2a51f;color:#1d2329;border:none;"
                                    "border-radius:18px;padding:6px 14px}")
        self.mehrzeit.setToolTip("Mama oder Papa um 15 Minuten mehr bitten")
        self.mehrzeit.clicked.connect(self.mehr_zeit)
        sb.addSpacing(10)
        sb.addWidget(self.mehrzeit)
        oben.addWidget(self.sonnebox)
        v.addLayout(oben)

        self.zurueck = QPushButton("⬅️  Zurück")
        f = self.zurueck.font(); f.setPixelSize(30); f.setBold(True); self.zurueck.setFont(f)
        self.zurueck.setStyleSheet("QPushButton{background:#fff;color:#1f3557;border-radius:22px;"
                                   "padding:10px 26px;border-bottom:6px solid rgba(0,0,0,.12)}")
        self.zurueck.clicked.connect(lambda: self.zeige(None))
        zl = QHBoxLayout(); zl.addWidget(self.zurueck); zl.addStretch(1)
        v.addLayout(zl)

        self.flaeche = QWidget(); self.flaeche.setStyleSheet("background:transparent")
        self.raster = QGridLayout(self.flaeche); self.raster.setSpacing(30)
        scroll = QScrollArea(); scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea{background:transparent}")
        scroll.viewport().setStyleSheet("background:transparent")
        scroll.setWidget(self.flaeche)
        v.addWidget(scroll, 1)

        unten = QHBoxLayout(); unten.addStretch(1)
        for text, tip, fn in (("⏻  Herunterfahren", "Den Computer ausschalten", self.herunterfahren),
                              ("🚪  Abmelden", "Abmelden – dann kann sich jemand anderes anmelden", self.abmelden)):
            kn = QPushButton(text)
            kn.setToolTip(tip); kn.setAccessibleName(text)
            kn.setCursor(Qt.CursorShape.PointingHandCursor)
            kn.setMinimumHeight(64)
            kn.setStyleSheet("QPushButton{background:rgba(255,255,255,.75);color:#1f3557;"
                             "border-radius:22px;padding:10px 28px;font-size:24px;font-weight:bold;"
                             "border-bottom:5px solid rgba(0,0,0,.12)}"
                             "QPushButton:pressed{background:#ffe9a8}")
            kn.clicked.connect(fn)
            unten.addWidget(kn)
        v.addLayout(unten)

        self.zeige(None)
        self.uhr = QTimer(self); self.uhr.timeout.connect(self.zeit_neu); self.uhr.start(30000)
        self.zeit_neu()
        self.lautuhr = QTimer(self); self.lautuhr.timeout.connect(self.laut_pruefen); self.lautuhr.start(4000)
        self.laut_pruefen()
        self.laeuft = []
        self.knopf = NachHause(self.nach_hause)
        self.knopfuhr = QTimer(self); self.knopfuhr.timeout.connect(self.knopf_pruefen); self.knopfuhr.start(1500)

    # ---- Seiten ----
    def zeige(self, gruppe):
        while self.raster.count():
            w = self.raster.takeAt(0).widget()
            if w:
                w.hide(); w.setParent(None); w.deleteLater()
        if gruppe is None:
            self.titel.setText("Hallo %s!" % vorname(self.user))
            kacheln = kacheln_fuer(self.user)
            self.zurueck.hide()
        else:
            self.titel.setText("%s %s" % (gruppe.get("symbol", "🧩"), gruppe.get("gruppe", "")))
            kacheln = gruppe.get("kacheln") or []
            self.zurueck.show()
        erlaubt = erlaubte_apps(self.user)
        ws = [w for w in (self.mach_kachel(k, erlaubt, i) for i, k in enumerate(kacheln)) if w]
        # Keine „Hinzufügen“-Kachel (be4k): Kinder landeten sonst bei der Passwort-
        # abfrage. Eltern richten Kacheln im Kontrollzentrum ein.
        spalten = 3 if len(ws) <= 6 else 4     # bis 6 Kacheln groß, sonst 4 nebeneinander
        for c in range(4):
            self.raster.setColumnStretch(c, 1 if c < spalten else 0)
        for i, w in enumerate(ws):
            self.raster.addWidget(w, i // spalten, i % spalten)
        self.raster.setRowStretch((len(ws) - 1) // spalten + 1, 1)   # Rest nach unten

    def mach_kachel(self, k, erlaubt, i):
        farbe = FARBEN[i % len(FARBEN)]
        if "gruppe" in k:
            name = k.get("gruppe") or "Gruppe"
            w = Kachel(name, emoji_icon(k.get("symbol", "🧩")), farbe, vorlesen=name)
            w.clicked.connect(lambda _=False, g=k, n=name: (sprich(n), self.zeige(g)))
            return w
        app = k.get("app", "")
        if app not in erlaubt:                 # nicht installiert oder fürs Alter gesperrt
            return None
        info = app_info(app)
        name = k.get("name") or info["name"]
        ic = emoji_icon(k["symbol"]) if k.get("symbol") else icon_fuer(info["icon"])
        if ic.isNull():
            ic = emoji_icon("⭐")
        w = Kachel(name, ic, farbe, vorlesen=name)
        w.clicked.connect(lambda _=False, a=app, n=name: (sprich(n), self.app_starten(a)))
        return w

    # ---- Programme und „Nach Hause“ ----
    def app_starten(self, app):
        pr = starte(app)
        if pr == "laeuft":
            # Schon offen (be4m): kein zweites Fenster – Startbildschirm geht zur Seite,
            # das laufende Programm kommt zum Vorschein; „Nach Hause“ bringt ihn zurück.
            self.showMinimized()
            QTimer.singleShot(800, self.knopf_pruefen)
        elif pr:
            self.laeuft.append(pr)
            QTimer.singleShot(800, self.knopf_pruefen)

    def knopf_pruefen(self):
        """Knopf zeigen, solange ein vom Startbildschirm gestartetes Programm läuft."""
        self.laeuft = [pr for pr in self.laeuft if pr.poll() is None]
        if self.laeuft:
            if not self.knopf.isVisible():
                self.knopf.show()
        elif self.knopf.isVisible():
            self.knopf.hide()

    def nach_hause(self):
        sprich("Nach Hause")
        for pr in self.laeuft:
            try:
                os.killpg(pr.pid, signal.SIGTERM)     # ganze Gruppe (auch Unterprozesse)
            except OSError:
                pass
        QTimer.singleShot(3000, self.aufraeumen)
        self.knopf.hide()
        self.showFullScreen(); self.raise_(); self.activateWindow()
        self.zeige(None)

    def aufraeumen(self):
        """Wer sich nach 3 Sekunden nicht beendet hat, wird beendet."""
        for pr in self.laeuft:
            if pr.poll() is None:
                try:
                    os.killpg(pr.pid, signal.SIGKILL)
                except OSError:
                    pass
        self.knopf_pruefen()

    # ---- Restzeit ----
    def mehr_zeit(self):
        sprich("Mehr Zeit")
        try:
            subprocess.Popen(["/usr/local/bin/serafino-mehr-zeit.py"], start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass
        QTimer.singleShot(20000, self.zeit_neu)

    def zeit_neu(self):
        z = restzeit(self.user)
        if not z:
            self.sonnebox.hide()
            return
        uebrig, genutzt = z
        ges = uebrig + genutzt
        if ges <= 0 or uebrig > 86000:         # keine Begrenzung
            self.sonnebox.hide()
            return
        self.sonnebox.show()
        a = uebrig / ges
        self.sonne.setze(a)
        self.zeittext.setText("Noch viel Zeit" if a > 0.5 else
                              "Noch ein bisschen" if a > 0.2 else "Bald ist Schluss")

    # ---- Lautstärke ----
    def laut_pruefen(self):
        """Balken aktualisieren (nur Anzeige – es wird nichts zurückgeregelt)."""
        v = lautstaerke()
        if v is None:
            self.lautbox.hide()
            return
        self.lautbox.show()
        self.balken.setze(min(1.0, v / self.lautmax))
        self.leiser.setEnabled(v > 0)
        self.lauter.setEnabled(v < self.lautmax)

    def laut_aendern(self, schritt):
        v = lautstaerke()
        if v is None:
            return
        neu = max(0, min(self.lautmax, v + schritt))
        if schritt > 0 and neu < LAUT_SCHRITT:
            neu = min(self.lautmax, LAUT_SCHRITT)
        setze_lautstaerke(neu)
        piep()
        self.laut_pruefen()

    def bearbeiten(self):
        Editor(self.user, self).exec()
        self.lautmax = max_lautstaerke(self.user)
        self.zeige(None)
        self.laut_pruefen()

    def _sitzung_beenden(self, methode, rueckfall):
        """Über KDE (ohne Rückfrage); klappt das nicht, über systemd/logind."""
        try:
            ok = subprocess.run(["dbus-send", "--session", "--type=method_call",
                                 "--dest=org.kde.Shutdown", "/Shutdown",
                                 "org.kde.Shutdown." + methode],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                timeout=5).returncode == 0
        except (OSError, subprocess.SubprocessError):
            ok = False
        if not ok:
            try:
                subprocess.Popen(rueckfall, start_new_session=True,
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except OSError:
                pass

    def herunterfahren(self):
        sprich("Tschüss")
        self._sitzung_beenden("logoutAndShutdown", ["systemctl", "poweroff"])

    def abmelden(self):
        sprich("Tschüss")
        self._sitzung_beenden("logout", ["loginctl", "terminate-user", self.user])


# ---------------------------------------------------------------- Editor (Eltern)
class Editor(QDialog):
    """Kacheln eines Kindes einrichten. Speichern fragt nach dem Eltern-Passwort."""

    def __init__(self, user, parent=None):
        super().__init__(parent)
        self.user = user
        self.setWindowTitle("Startbildschirm von %s einrichten" % vorname(user))
        self.resize(900, 600)
        if os.path.exists(LOGO):
            self.setWindowIcon(QIcon(LOGO))
        conf = lade_conf(user)
        v = QVBoxLayout(self)
        a = alter(user)
        info = QLabel("<b>%s</b>%s – links die Programme, die zum Alter passen. Mit „→“ auf den "
                      "Startbildschirm legen, mit „Neue Gruppe“ mehrere zusammenfassen (z. B. „Spielen“). "
                      "Speichern fragt nach dem Eltern-Passwort."
                      % (vorname(user), " (%d Jahre)" % a if a is not None else ""))
        info.setWordWrap(True)
        v.addWidget(info)

        h = QHBoxLayout(); v.addLayout(h, 1)
        self.apps = QListWidget()
        for n, titel in erlaubte_apps(user).items():
            it = QListWidgetItem(icon_fuer((app_info(n) or {}).get("icon", "")), titel)
            it.setData(Qt.ItemDataRole.UserRole, n)
            self.apps.addItem(it)
        h.addWidget(self.apps, 1)

        mitte = QVBoxLayout(); mitte.addStretch(1)
        for text, fn in (("→", self.hinzu), ("←", self.weg), ("▲", lambda: self.schiebe(-1)),
                         ("▼", lambda: self.schiebe(1))):
            b = QPushButton(text); b.setFixedWidth(52); b.clicked.connect(fn); mitte.addWidget(b)
        mitte.addStretch(1)
        h.addLayout(mitte)

        self.baum = QTreeWidget(); self.baum.setHeaderLabel("Auf dem Startbildschirm")
        self.baum.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.baum.itemDoubleClicked.connect(self.umbenennen)
        h.addWidget(self.baum, 1)
        for k in kacheln_fuer(user):
            self.baum.addTopLevelItem(self.item_aus(k))
        self.baum.expandAll()

        knoepfe = QHBoxLayout()
        gruppe = QPushButton("📁 Neue Gruppe"); gruppe.clicked.connect(self.neue_gruppe)
        umb = QPushButton("✏️ Umbenennen"); umb.clicked.connect(lambda: self.umbenennen(self.baum.currentItem()))
        knoepfe.addWidget(gruppe); knoepfe.addWidget(umb); knoepfe.addStretch(1)
        knoepfe.addWidget(QLabel("Einfache Oberfläche:"))
        self.modus = QComboBox()
        for wert, text in (("auto", "automatisch bis %d Jahre" % AUTO_BIS), ("an", "immer"), ("aus", "nie")):
            self.modus.addItem(text, wert)
        self.modus.setCurrentIndex(max(0, self.modus.findData(conf.get("modus", "auto"))))
        knoepfe.addWidget(self.modus)
        v.addLayout(knoepfe)

        unten = QHBoxLayout(); unten.addStretch(1)
        ab = QPushButton("Abbrechen"); ab.clicked.connect(self.reject)
        sp = QPushButton(QIcon.fromTheme("document-save"), "Speichern"); sp.clicked.connect(self.speichern)
        unten.addWidget(ab); unten.addWidget(sp)
        v.addLayout(unten)

    def item_aus(self, k):
        if "gruppe" in k:
            it = QTreeWidgetItem(["%s %s" % (k.get("symbol", "🧩"), k.get("gruppe", "Gruppe"))])
            it.setData(0, Qt.ItemDataRole.UserRole, {"gruppe": k.get("gruppe", "Gruppe"),
                                                     "symbol": k.get("symbol", "🧩")})
            it.setFlags(it.flags() | Qt.ItemFlag.ItemIsDropEnabled)
            for c in k.get("kacheln") or []:
                if "app" in c:
                    it.addChild(self.item_aus(c))
            return it
        info = app_info(k.get("app", "")) or {"name": k.get("app", "?"), "icon": ""}
        it = QTreeWidgetItem([k.get("name") or info["name"]])
        it.setIcon(0, icon_fuer(info["icon"]))
        d = {"app": k.get("app")}
        if k.get("name"):
            d["name"] = k["name"]
        it.setData(0, Qt.ItemDataRole.UserRole, d)
        it.setFlags(it.flags() & ~Qt.ItemFlag.ItemIsDropEnabled)
        return it

    def hinzu(self):
        a = self.apps.currentItem()
        if not a:
            return
        neu = self.item_aus({"app": a.data(Qt.ItemDataRole.UserRole)})
        ziel = self.baum.currentItem()
        if ziel and "gruppe" in (ziel.data(0, Qt.ItemDataRole.UserRole) or {}):
            ziel.addChild(neu); ziel.setExpanded(True)
        elif ziel and ziel.parent():
            ziel.parent().addChild(neu)
        else:
            self.baum.addTopLevelItem(neu)

    def weg(self):
        it = self.baum.currentItem()
        if not it:
            return
        (it.parent() or self.baum.invisibleRootItem()).removeChild(it)

    def schiebe(self, d):
        it = self.baum.currentItem()
        if not it:
            return
        p = it.parent() or self.baum.invisibleRootItem()
        i = p.indexOfChild(it); j = i + d
        if 0 <= j < p.childCount():
            p.takeChild(i); p.insertChild(j, it); self.baum.setCurrentItem(it)

    def neue_gruppe(self):
        name, ok = QInputDialog.getText(self, "Neue Gruppe", "Name der Gruppe (z. B. Spielen):")
        if not ok or not name.strip():
            return
        sym, ok = QInputDialog.getItem(self, "Neue Gruppe", "Bild:", GRUPPEN_SYMBOLE, 0, False)
        if not ok:
            return
        it = self.item_aus({"gruppe": name.strip()[:30], "symbol": sym, "kacheln": []})
        self.baum.addTopLevelItem(it); self.baum.setCurrentItem(it)

    def umbenennen(self, it, *_):
        if not it:
            return
        d = dict(it.data(0, Qt.ItemDataRole.UserRole) or {})
        alt = d.get("gruppe") or d.get("name") or it.text(0)
        name, ok = QInputDialog.getText(self, "Umbenennen", "Neuer Name (wird auch vorgelesen):", text=alt)
        if not ok or not name.strip():
            return
        name = name.strip()[:30]
        if "gruppe" in d:
            d["gruppe"] = name; it.setText(0, "%s %s" % (d.get("symbol", "🧩"), name))
        else:
            d["name"] = name; it.setText(0, name)
        it.setData(0, Qt.ItemDataRole.UserRole, d)

    def sammle(self):
        def kachel(it):
            d = dict(it.data(0, Qt.ItemDataRole.UserRole) or {})
            if "gruppe" in d:
                d["kacheln"] = [kachel(it.child(i)) for i in range(it.childCount())
                                if "app" in (it.child(i).data(0, Qt.ItemDataRole.UserRole) or {})]
            return d
        root = self.baum.invisibleRootItem()
        return {"modus": self.modus.currentData(),
                "max_lautstaerke": 100,
                "kacheln": [kachel(root.child(i)) for i in range(root.childCount())]}

    def speichern(self):
        daten = json.dumps(self.sammle(), ensure_ascii=False)
        try:
            r = subprocess.run(HELPER + ["ks-save", self.user], input=daten, text=True,
                               capture_output=True)
        except OSError as e:
            QMessageBox.warning(self, "Speichern", str(e)); return
        if r.returncode == 0:
            self.accept()
        elif r.returncode in (126, 127):
            QMessageBox.information(self, "Speichern", "Abgebrochen – ohne Eltern-Passwort wird nichts gespeichert.")
        else:
            QMessageBox.warning(self, "Speichern", "Hat nicht geklappt: " + (r.stderr or "").strip()[:300])


# ---------------------------------------------------------------- Start
def main():
    args = sys.argv[1:]
    user = pwd.getpwuid(os.getuid()).pw_name
    if args[:1] == ["--auto"] and not aktiv_fuer(user):
        if kwin_regeln_da():               # Konto hat keinen Startbildschirm (mehr): Regeln weg
            kwin_regeln(False)
        return 0
    app = QApplication(sys.argv)
    app.setApplicationName("pingulinux-kinderstart")
    app.setDesktopFileName("pingulinux-kinderstart")

    if args[:1] == ["--bearbeiten"]:
        ziel = args[1] if len(args) > 1 else ""
        if alter(ziel) is None:                # aus dem Kontrollzentrum: Kind auswählen
            try:
                kinder = sorted(n for n in os.listdir(PROFDIR) if alter(n) is not None)
            except OSError:
                kinder = []
            kinder = [k for k in kinder if subprocess.run(["id", k], capture_output=True).returncode == 0]
            if not kinder:
                QMessageBox.information(None, "Startbildschirm der Kleinen",
                                        "Es gibt noch keine Kinderkonten.")
                return 1
            namen = ["%s (%s, %d Jahre)" % (vorname(k), k, alter(k)) for k in kinder]
            wahl, ok = QInputDialog.getItem(None, "Startbildschirm der Kleinen",
                                            "Für welches Kind?", namen, 0, False)
            if not ok:
                return 1
            ziel = kinder[namen.index(wahl)]
        return 0 if Editor(ziel).exec() else 1

    # Nur einmal pro Konto: läuft er schon, holt ein zweiter Aufruf ihn nach vorn.
    key = "pingulinux-kinderstart-%d" % os.getuid()
    s = QLocalSocket(); s.connectToServer(key)
    if s.waitForConnected(300):
        s.write(b"zeigen"); s.flush(); s.waitForBytesWritten(300)
        return 0
    QLocalServer.removeServer(key)
    server = QLocalServer(); server.listen(key)

    win = Startbildschirm(user)
    g = app.primaryScreen().geometry() if app.primaryScreen() else None
    if g:
        kwin_regeln(True, g.x() + 24, g.y() + g.height() - KNOPF_GROESSE - 24)

    def nach_vorn():
        c = server.nextPendingConnection()
        if c:
            c.close()
        win.showFullScreen(); win.raise_(); win.activateWindow(); win.zeige(None)
    server.newConnection.connect(nach_vorn)
    win.showFullScreen()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
