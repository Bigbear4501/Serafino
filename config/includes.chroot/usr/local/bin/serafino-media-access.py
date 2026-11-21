#!/usr/bin/env python3
"""serafino-media-access.py  (läuft als root, über systemd)

Kamera und Mikrofon erst ab 10 Jahren.

So funktioniert es:
  - Kamera: Eine udev-Regel (72-serafino-media.rules) gibt Kameras
    (/dev/video*) nur noch der Gruppe „serafinomedia“ frei. Dieses Skript legt
    fest, wer in der Gruppe ist: alle Erwachsenen-Konten und Kinder ab 10.
  - Mikrofon (seit 17. Nov, b25): Für Kinder unter 10 liegt eine
    WirePlumber-Regel in /etc/serafino/pro-konto/KIND/wireplumber/, die alle
    Mikrofone abschaltet (auch Bluetooth). Lautsprecher und Kopfhörer bleiben.
    Früher sperrte die udev-Regel die Aufnahme-Geräte direkt – auf dem
    Surface verschwand damit die ganze Soundkarte, also auch der Ton.
    Wirkt ab der nächsten Anmeldung des Kindes.
  - Läuft beim Start, täglich und sobald sich ein Alter ändert. Am
    10. Geburtstag kommt das Kind automatisch in die Gruppe (wirkt ab der
    nächsten Anmeldung).
"""
import datetime, grp, os, pwd, re, subprocess, sys

DATA = os.environ.get("FINO_DATA", "/var/lib/serafino")
GROUP = "serafinomedia"
MIN_AGE = 10
DRY = "--dry-run" in sys.argv


def today():
    t = os.environ.get("FINO_TODAY")
    return datetime.date.fromisoformat(t) if t else datetime.date.today()


def age_from(text):
    s = text.strip()
    m = re.fullmatch(r"(\d{4})-(\d{1,2})(?:-(\d{1,2}))?", s)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3) or 1)
        t = today()
        return t.year - y - ((t.month, t.day) < (mo, d))
    if re.fullmatch(r"\d{1,3}", s):
        return int(s)
    return None


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return None


def kid_age(name):
    """Alter eines Kinderkontos, 0 wenn unbekannt; None wenn kein Kind."""
    b = read(os.path.join(DATA, "birth", name))
    p = read(os.path.join(DATA, "profiles", name))
    if b is None and p is None:
        return None
    age = age_from(b) if b else None
    if age is None and p:
        age = age_from(p)
    return age if age is not None else 0


PRO_KONTO = "/etc/serafino/pro-konto"
MIKRO_REGEL = "wireplumber/wireplumber.conf.d/90-serafino-kein-mikrofon.conf"
MIKRO_TEXT = """# Serafino: Mikrofon erst ab 10 Jahren (wird von serafino-media-access.py
# angelegt und wieder entfernt – bitte nicht von Hand ändern).
monitor.alsa.rules = [
  {
    matches = [ { node.name = "~alsa_input.*" } ]
    actions = { update-props = { node.disabled = true } }
  }
]
monitor.bluez.rules = [
  {
    matches = [ { node.name = "~bluez_input.*" } ]
    actions = { update-props = { node.disabled = true } }
  }
]
"""


def mikrofon(name, gesperrt):
    """WirePlumber-Regel für dieses Konto anlegen bzw. entfernen."""
    pfad = os.path.join(PRO_KONTO, name, MIKRO_REGEL)
    if gesperrt:
        try:
            if open(pfad, encoding="utf-8").read() == MIKRO_TEXT:
                return
        except OSError:
            pass
        if DRY:
            print("[dry-run] Mikrofon-Regel: " + pfad)
            return
        os.makedirs(os.path.dirname(pfad), mode=0o755, exist_ok=True)
        with open(pfad + ".neu", "w", encoding="utf-8") as f:
            f.write(MIKRO_TEXT)
        os.chmod(pfad + ".neu", 0o644)
        os.replace(pfad + ".neu", pfad)
    elif os.path.exists(pfad):
        if DRY:
            print("[dry-run] Mikrofon-Regel weg: " + pfad)
            return
        os.remove(pfad)


def sh(cmd):
    if DRY:
        print("[dry-run] " + " ".join(cmd))
        return
    subprocess.run(cmd, check=False)


def main():
    try:
        members = set(grp.getgrnam(GROUP).gr_mem)
    except KeyError:
        if DRY:
            members = set()
        else:
            subprocess.run(["groupadd", "--system", GROUP], check=False)
            members = set()
    for pw in pwd.getpwall():
        if not (1000 <= pw.pw_uid < 60000):
            continue
        # nur echte Anmelde-Konten (Ordner unter /home, normale Shell)
        if not pw.pw_dir.startswith("/home/") or pw.pw_shell.endswith(("nologin", "false")):
            continue
        age = kid_age(pw.pw_name)
        allowed = age is None or age >= MIN_AGE
        label = "Erwachsen" if age is None else "%d Jahre" % age
        print("%-16s %-10s Kamera/Mikrofon: %s" % (pw.pw_name, label, "frei" if allowed else "gesperrt"))
        mikrofon(pw.pw_name, not allowed)
        if allowed and pw.pw_name not in members:
            sh(["gpasswd", "-a", pw.pw_name, GROUP])
        elif not allowed and pw.pw_name in members:
            sh(["gpasswd", "-d", pw.pw_name, GROUP])


if __name__ == "__main__":
    main()
