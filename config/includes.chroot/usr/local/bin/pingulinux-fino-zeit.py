#!/usr/bin/env python3
"""Fino sagt Bescheid, wenn die Bildschirmzeit bald um ist.

Läuft im Kinderkonto beim Anmelden mit (Autostart). Liest die Restzeit, die
pingulinux-restzeit.sh jede Minute nach /run/pingulinux/restzeit/BENUTZER
schreibt („übrig_sek genutzt_sek“). Bei 15, 5 und 1 Minute erscheint einmal
Fino (pingulinux-kind-hinweis.py) und sagt es auch laut.

Jede Stufe nur einmal pro Tag: Merker in ~/.local/state/pingulinux/fino-zeit-DATUM.
Ohne Zeitbegrenzung (oder ohne Timekpr) passiert nichts. Bei den Hinweisen gibt
es den Knopf „Mehr Zeit bitte“ (be15).

Bildschirm-Pausen (be16): Nach 30 Minuten (bis 6 Jahre), 40 Minuten (7–9) bzw.
45 Minuten (ab 10) am Stück erinnert Fino ans Aufstehen. Ist der Bildschirm
mindestens 5 Minuten gesperrt (oder der Computer im Ruhezustand), zählt das
als Pause und die Uhr beginnt von vorn. Gilt auch ohne Zeitbegrenzung.
Aus für ein Kind: Datei /var/lib/pingulinux/keine-pausen/KIND.
"""
import datetime
import os
import pwd
import subprocess
import sys
import time

ZEITDIR = "/run/pingulinux/restzeit"
HINWEIS = "/usr/local/bin/pingulinux-kind-hinweis.py"
STUFEN = [
    (15, "Noch 15 Minuten!", "Dann ist Bildschirm-Pause. Such dir schon mal aus, was du noch machen möchtest."),
    (5, "Noch 5 Minuten!", "Bald ist Schluss – speicher dein Bild oder dein Spiel."),
    (1, "Noch 1 Minute!", "Gleich ist die Zeit um. Tschüss und bis bald! 👋"),
]
TAKT = 20          # Sekunden zwischen zwei Blicken auf die Restzeit
PAUSE_GENUG = 5 * 60   # so lange gesperrt/aus = Pause gemacht
PAUSE_TEXT = ("Zeit für eine Pause! 🤸",
              "Steh auf, streck dich und schau mal aus dem Fenster. Trink einen Schluck Wasser – "
              "danach geht's weiter.")


def pausen_minuten(user):
    if os.path.exists(os.path.join("/var/lib/pingulinux/keine-pausen", user)):
        return None
    try:
        alter = int(open(os.path.join("/var/lib/pingulinux/profiles", user)).read().split()[0])
    except (OSError, ValueError, IndexError):
        alter = 8
    return 30 if alter <= 6 else 40 if alter <= 9 else 45


def gesperrt():
    sid = os.environ.get("XDG_SESSION_ID", "")
    try:
        r = subprocess.run(["loginctl", "show-session", sid, "-p", "LockedHint", "--value"] if sid else
                           ["false"], capture_output=True, text=True, timeout=5)
        return r.stdout.strip() == "yes"
    except (OSError, subprocess.SubprocessError):
        return False


def ich():
    return pwd.getpwuid(os.getuid()).pw_name


def ist_kind(user):
    return os.path.exists(os.path.join("/var/lib/pingulinux/profiles", user))


def restzeit(user):
    """Übrige Sekunden oder None (keine Begrenzung / unbekannt)."""
    try:
        teile = open(os.path.join(ZEITDIR, user)).read().split()
        uebrig, genutzt = int(teile[0]), int(teile[1])
    except (OSError, ValueError, IndexError):
        return None
    if uebrig > 86000 or uebrig + genutzt <= 0:
        return None
    return uebrig


def merker():
    d = os.path.join(os.path.expanduser("~"), ".local", "state", "pingulinux")
    os.makedirs(d, exist_ok=True)
    return os.path.join(d, "fino-zeit-%s" % datetime.date.today().isoformat())


def schon(stufe):
    try:
        return str(stufe) in open(merker()).read().split()
    except OSError:
        return False


def merken(stufe):
    try:
        with open(merker(), "a") as f:
            f.write("%d\n" % stufe)
    except OSError:
        pass


def main():
    user = ich()
    if not ist_kind(user):
        return 0
    pause_min = pausen_minuten(user)
    am_stueck = 0.0          # Sekunden Bildschirm am Stück
    gesperrt_seit = None
    letzter = time.monotonic()
    while True:
        jetzt = time.monotonic()
        schritt = jetzt - letzter
        letzter = jetzt
        # ---- Bildschirm-Pausen (be16)
        if pause_min:
            if schritt > PAUSE_GENUG:                 # Ruhezustand / lange weg
                am_stueck = 0.0
            elif gesperrt():
                gesperrt_seit = gesperrt_seit or jetzt
                if jetzt - gesperrt_seit >= PAUSE_GENUG:
                    am_stueck = 0.0
            else:
                gesperrt_seit = None
                am_stueck += schritt
                if am_stueck >= pause_min * 60:
                    am_stueck = 0.0
                    try:
                        subprocess.Popen([HINWEIS, "--text", PAUSE_TEXT[0], "--klein", PAUSE_TEXT[1], "--zu", "30"],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except OSError:
                        pass
        # ---- Restzeit-Hinweise
        s = restzeit(user)
        if s is not None:
            minuten = s / 60.0
            # nur die kleinste erreichte Stufe zeigen (wer erst bei 4 Min. anmeldet, bekommt nur „5“)
            faellig = [st for st in STUFEN if minuten <= st[0] + 0.5 and not schon(st[0])]
            if faellig:
                stufe, gross, klein = min(faellig, key=lambda x: x[0])
                for st in faellig:
                    merken(st[0])
                if minuten > 0.2:
                    try:
                        subprocess.Popen([HINWEIS, "--text", gross, "--klein", klein, "--zu", "25", "--mehrzeit"],
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    except OSError:
                        pass
        time.sleep(TAKT)


if __name__ == "__main__":
    if "--test" in sys.argv:      # Eltern: Fino-Hinweis einmal ansehen
        subprocess.call([HINWEIS, "--text", STUFEN[1][1], "--klein", STUFEN[1][2], "--zu", "25", "--mehrzeit"])
        sys.exit(0)
    if "--pause-test" in sys.argv:   # Eltern: Pausen-Hinweis einmal ansehen
        subprocess.call([HINWEIS, "--text", PAUSE_TEXT[0], "--klein", PAUSE_TEXT[1], "--zu", "30"])
        sys.exit(0)
    sys.exit(main())
