#!/usr/bin/env python3
"""serafino-spielzeit.py - Lernprogramme zählen nicht zur Bildschirmzeit (bz7).

Nutzt „PlayTime“ von Timekpr-nExT im Modus „Override“: Die Bildschirmzeit
läuft nur, solange ein Spiel, YouTube Kids oder Firefox offen ist. Lernen,
Malen, Schreiben und alles andere zählt nicht (Uhrzeiten gelten trotzdem).

Ab Werk für jedes Kinderkonto an. Ausschalten pro Kind im Fenster
„Bildschirmzeit“: dann liegt /var/lib/pingulinux/alles-zaehlt/KIND und es
zählt wie früher jede Minute.

  serafino-spielzeit.py --alle          alle Kinderkonten anwenden (root)
  serafino-spielzeit.py KIND an|aus     ein Kind umstellen (root)
  serafino-spielzeit.py --liste         zeigen, was als Spiel zählt

Was zählt, wird aus dem Startmenü gelesen (Kategorie „Game“ ohne „Education“)
und nach jeder Installation neu angewendet (APT-Hook, App Store).
"""
import configparser
import glob
import os
import re
import subprocess
import sys

PROFDIR = "/var/lib/pingulinux/profiles"
AUS_DIR = "/var/lib/pingulinux/alles-zaehlt"
TK_CONF = "/etc/timekpr/timekpr.conf"
APPDIRS = ["/usr/share/applications", "/usr/local/share/applications"]
FLATPAK_APPS = "/var/lib/flatpak/exports/share/applications"
# immer gezählt (Videos und Internet)
# Timekpr vergleicht so (b30, aus dem Quelltext von 0.5.4): der Name muss das
# ganze Programm sein oder am Ende eines Pfads stehen – „/NAME“ am Ende oder
# „/NAME “ mit Leerzeichen danach, mit „Erweiterter Aktivitätsüberwachung“
# auch irgendwo in der Befehlszeile. YouTube Kids ist ein Python-Skript
# („python3 /usr/local/bin/pingulinux-youtube-kids-viewer.py“) – also muss
# „.py“ mit in die Maske. Firefox heißt bei Debian „firefox-esr“.
IMMER = [("pingulinux-youtube-kids-viewer.py", "YouTube Kids"),
         ("pingulinux-youtube-kids-viewer-gtk.py", "YouTube Kids (alt)"),
         ("firefox-esr", "Firefox"), ("firefox", "Firefox")]


def sauber(t, erlaubt=r"[^A-Za-z0-9._-]"):
    return re.sub(erlaubt, "", t)


def spiele():
    """Liste (Maske, Beschreibung) aller Spiele im Startmenü."""
    out = list(IMMER)
    gesehen = {m for m, _ in out}
    for d in APPDIRS + [FLATPAK_APPS]:
        for p in sorted(glob.glob(os.path.join(d, "*.desktop"))):
            c = configparser.RawConfigParser(strict=False, interpolation=None)
            try:
                c.read(p, encoding="utf-8")
                e = c["Desktop Entry"]
            except (configparser.Error, KeyError, UnicodeDecodeError):
                continue
            kat = (e.get("Categories") or "").split(";")
            if "Game" not in kat or "Education" in kat:
                continue
            name = re.sub(r"[\[\];]", "", e.get("Name[de]") or e.get("Name") or "")
            masken = []
            if d == FLATPAK_APPS:
                app_id = os.path.basename(p)[:-8]
                masken.append(sauber(app_id))           # steht in der Befehlszeile von bwrap
                try:
                    meta = subprocess.run(["flatpak", "info", "-m", app_id], capture_output=True,
                                          text=True, timeout=20).stdout
                    m = re.search(r"^command=(\S+)", meta, re.M)
                    if m:
                        masken.append(sauber(os.path.basename(m.group(1))))
                except (OSError, subprocess.SubprocessError):
                    pass
            else:
                teile = (e.get("Exec") or "").split()
                while teile and (teile[0] == "env" or "=" in teile[0]):
                    teile = teile[1:]
                if teile:
                    masken.append(sauber(os.path.basename(teile[0])))
            for m in masken:
                if len(m) >= 3 and m not in gesehen:
                    gesehen.add(m)
                    out.append((m, name or m))
    return out


def kinder():
    try:
        return sorted(os.listdir(PROFDIR))
    except OSError:
        return []


def tk(*args):
    return subprocess.run(["timekpra"] + list(args), capture_output=True, text=True)


def global_an():
    """PlayTime und die Suche in der Befehlszeile in Timekpr einschalten."""
    try:
        t = open(TK_CONF).read()
    except OSError:
        return False
    neu = t
    for k in ("TIMEKPR_PLAYTIME_ENABLED", "TIMEKPR_PLAYTIME_ENHANCED_ACTIVITY_MONITOR_ENABLED"):
        if re.search(r"^%s\s*=" % k, neu, re.M):
            neu = re.sub(r"^%s\s*=.*$" % k, "%s = True" % k, neu, flags=re.M)
        else:
            if "[PLAYTIME]" not in neu:
                neu += "\n[PLAYTIME]\n"
            neu = neu.replace("[PLAYTIME]", "[PLAYTIME]\n%s = True" % k, 1)
    if neu != t:
        with open(TK_CONF, "w") as f:
            f.write(neu)
        subprocess.run(["systemctl", "try-restart", "timekpr.service"], capture_output=True)
    return True


def anwenden(kind, liste):
    if not os.path.isfile(os.path.join(PROFDIR, kind)):
        return "kein Kinderkonto"
    if os.path.exists(os.path.join(AUS_DIR, kind)):
        tk("--setplaytimelimitoverride", kind, "false")
        tk("--setplaytimeenabled", kind, "false")
        return "alles zählt"
    akt = ";".join("%s[%s]" % (m, b) for m, b in liste)
    for args in (("--setplaytimeactivities", kind, akt),
                 ("--setplaytimealloweddays", kind, "1;2;3;4;5;6;7"),
                 ("--setplaytimelimits", kind, ";".join(["86400"] * 7)),   # im Override-Modus ohne Wirkung
                 ("--setplaytimeunaccountedintervalsflag", kind, "true"),
                 ("--setplaytimeenabled", kind, "true"),
                 ("--setplaytimelimitoverride", kind, "true")):
        r = tk(*args)
        if r.returncode != 0:
            return "Fehler bei %s: %s" % (args[0], (r.stderr or r.stdout).strip()[:200])
    return "nur Spiele, Videos und Internet zählen (%d Einträge)" % len(liste)


def main():
    a = sys.argv[1:]
    if a[:1] == ["--liste"]:
        for m, b in spiele():
            print("%-40s %s" % (m, b))
        return 0
    if os.geteuid() != 0:
        sys.exit("Nur als root.")
    if not global_an():
        print("Timekpr ist nicht installiert – nichts zu tun.")
        return 0
    if len(a) == 2 and a[1] in ("an", "aus"):
        kind = a[0]
        if not re.fullmatch(r"[a-z_][a-z0-9_-]*", kind) or not os.path.isfile(os.path.join(PROFDIR, kind)):
            sys.exit("Kein Kinderkonto: %s" % kind)
        os.makedirs(AUS_DIR, exist_ok=True)
        merker = os.path.join(AUS_DIR, kind)
        if a[1] == "aus":
            open(merker, "w").close()
        elif os.path.exists(merker):
            os.remove(merker)
        print("%s: %s" % (kind, anwenden(kind, spiele())))
        return 0
    if a[:1] == ["--alle"]:
        liste = spiele()
        for k in kinder():
            print("%s: %s" % (k, anwenden(k, liste)))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
