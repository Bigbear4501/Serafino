#!/usr/bin/python3 -I
"""serafino-wlan-alle-root.py UUID  (be4o; als root über pkexec, Passwort auf stdin)

Macht ein gespeichertes WLAN für alle Benutzer verfügbar:
  - [connection] permissions=…  entfällt  (sonst darf nur das eine Konto verbinden)
  - [wifi-security] psk-flags   entfällt  (= 0: Passwort liegt im System statt in
                                           der KDE-Brieftasche), psk wird gesetzt
Die Verbindungsdatei in /etc/NetworkManager/system-connections bleibt nur für root
lesbar (0600). Aufruf nur von serafino-wlan-alle.sh aus einem Eltern-Konto (sudo).
"""
import configparser
import grp
import os
import pwd
import re
import subprocess
import sys
import tempfile

ORDNER = "/etc/NetworkManager/system-connections/"


def stopp(text):
    print("serafino-wlan-alle: " + text, file=sys.stderr)
    sys.exit(1)


def ist_eltern(uid):
    try:
        name = pwd.getpwuid(uid).pw_name
    except KeyError:
        return False
    if os.path.exists("/var/lib/pingulinux/profiles/" + name):
        return False
    try:
        g = grp.getgrnam("sudo")
    except KeyError:
        return False
    return name in g.gr_mem or pwd.getpwnam(name).pw_gid == g.gr_gid


def schluessel_esc(v):
    """Wert für eine GKeyFile-Datei (NetworkManager-Keyfile) maskieren."""
    v = v.replace("\\", "\\\\").replace("\t", "\\t")
    if v.startswith(" "):
        v = "\\s" + v[1:]
    return v


def main():
    uuid = sys.argv[1] if len(sys.argv) > 1 else ""
    if not re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", uuid):
        stopp("Kennung?")
    try:
        uid = int(os.environ.get("PKEXEC_UID", ""))
    except ValueError:
        stopp("nur über pkexec")
    if not ist_eltern(uid):
        stopp("nur für Eltern-Konten")

    psk = sys.stdin.readline().rstrip("\n")
    if psk and not (re.fullmatch(r"[\x20-\x7e]{8,63}", psk) or re.fullmatch(r"[0-9a-fA-F]{64}", psk)):
        stopp("WLAN-Passwort hat ein unerwartetes Format")

    # Datei zur Verbindung finden
    r = subprocess.run(["nmcli", "-t", "-f", "UUID,FILENAME", "connection", "show"],
                       capture_output=True, text=True, env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"})
    datei = ""
    for zeile in r.stdout.splitlines():
        u, _, f = zeile.partition(":")
        if u.lower() == uuid.lower():
            datei = re.sub(r"\\(.)", r"\1", f)
            break
    datei = os.path.realpath(datei) if datei else ""
    if not datei.startswith(ORDNER) or not os.path.isfile(datei):
        stopp("Verbindungsdatei nicht gefunden")

    kf = configparser.RawConfigParser(strict=False, delimiters=("=",), comment_prefixes=("#",),
                                      inline_comment_prefixes=None, interpolation=None)
    kf.optionxform = str
    kf.read(datei, encoding="utf-8")
    if not kf.has_section("connection") or kf.get("connection", "type", fallback="") not in ("wifi", "802-11-wireless"):
        stopp("kein WLAN")

    kf.remove_option("connection", "permissions")
    if kf.has_section("wifi-security"):
        km = kf.get("wifi-security", "key-mgmt", fallback="")
        if km in ("wpa-psk", "sae"):
            if psk:
                kf.set("wifi-security", "psk", schluessel_esc(psk))
            elif not kf.get("wifi-security", "psk", fallback=""):
                stopp("kein WLAN-Passwort")
            kf.remove_option("wifi-security", "psk-flags")
        elif km not in ("", "owe"):
            stopp("Art %s wird nicht unterstützt" % km)

    fd, tmp = tempfile.mkstemp(dir=ORDNER, prefix=".serafino-")
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            kf.write(f, space_around_delimiters=False)
        os.replace(tmp, datei)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    subprocess.run(["nmcli", "connection", "load", datei], capture_output=True,
                   env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"})


if __name__ == "__main__":
    main()
