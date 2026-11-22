#!/bin/bash
#
# serafino-delete-user.sh  (als root, via pkexec)
# Aufruf: BENUTZER
# Loescht ein Konto samt Home-Ordner und raeumt alle Serafino-Reste auf
# (Altersprofil, Programmsperren, Bildschirmzeit, Profilbild, Hosts-Sperre).

U="$1"
CALLER_UID="${PKEXEC_UID:-}"

[ -n "$U" ] || { echo "Es wurde kein Konto angegeben."; exit 2; }
UID_N=$(id -u "$U" 2>/dev/null) || { echo "Das Konto '$U' gibt es nicht."; exit 3; }
if [ "$UID_N" -lt 1000 ] || [ "$UID_N" -ge 60000 ]; then
    echo "Dieses Konto darf hier nicht gelöscht werden."; exit 3
fi
if [ -n "$CALLER_UID" ] && [ "$UID_N" = "$CALLER_UID" ]; then
    echo "Du kannst nicht das Konto löschen, mit dem du gerade angemeldet bist."; exit 3
fi
# Nie das letzte Administrator-Konto loeschen
if id -nG "$U" | tr ' ' '\n' | grep -qx sudo; then
    ADMINS=$(getent group sudo | cut -d: -f4 | tr ',' '\n' | grep -c .)
    if [ "$ADMINS" -le 1 ]; then
        echo "Das ist das einzige Administrator-Konto und darf nicht gelöscht werden."; exit 3
    fi
fi

# Programmsperren (ACLs) des Kontos entfernen, damit eine spaetere neue
# Benutzer-Nummer nicht versehentlich gesperrt wird
python3 - "$U" <<'PY' 2>/dev/null
import json, os, shutil, subprocess, sys
user = sys.argv[1]
cmds = {"/usr/bin/xfce4-terminal", "/usr/bin/konsole"}
for src in ("/usr/share/serafino/store-apps.json", "/usr/share/serafino/app-ages.json"):
    try:
        for e in json.load(open(src, encoding="utf-8")):
            if e.get("cmd"):
                cmds.add(e["cmd"])
            if e.get("flatpak"):
                d = os.path.join("/var/lib/flatpak/app", e["flatpak"])
                if os.path.isdir(d):
                    subprocess.run(["setfacl", "-x", "u:%s" % user, d], capture_output=True)
    except Exception:
        pass
for cmd in cmds:
    path = cmd if cmd.startswith("/") else shutil.which(cmd, path="/usr/bin:/usr/games:/usr/local/bin:/bin")
    if path and os.path.exists(path):
        subprocess.run(["setfacl", "-x", "u:%s" % user, os.path.realpath(path)], capture_output=True)
PY

# Angemeldete Sitzungen und Prozesse des Kontos beenden
loginctl terminate-user "$U" >/dev/null 2>&1
pkill -KILL -u "$U" >/dev/null 2>&1
sleep 1

# bz37: Kinder-Ordner ist „noexec“ auf sich selbst eingehängt und der
# Flatpak-Ordner darin unveränderlich (chattr +i). Beides verhinderte das
# Löschen des Ordners – das Konto war weg, aber es kam eine Fehlermeldung.
# Deshalb vorher aushängen und den Schutz aufheben.
H=$(getent passwd "$U" | cut -d: -f6)
case "$H" in
    /home/?*)
        for _ in 1 2 3 4; do
            mountpoint -q "$H" 2>/dev/null || break
            umount "$H" 2>/dev/null || umount -l "$H" 2>/dev/null || break
        done
        chattr -R -i "$H" 2>/dev/null
        ;;
    *) H="" ;;
esac
umount -l "/run/user/$UID_N" 2>/dev/null
rm -f "/run/serafino/noexec-$U"

# Konto loeschen
OUT=$(deluser --remove-home "$U" 2>&1) || OUT2=$(userdel -r -f "$U" 2>&1)
if id "$U" >/dev/null 2>&1; then
    echo "Das Konto konnte nicht gelöscht werden:"
    echo "$OUT"; echo "${OUT2:-}"
    exit 4
fi
# Konto ist weg – übrig gebliebenen Ordner noch entfernen
[ -n "$H" ] && [ -d "$H" ] && rm -rf "$H" 2>/dev/null

# Reste aufraeumen
case "$U" in */*|.*) exit 0 ;; esac
rm -f "/var/lib/serafino/profiles/$U" "/var/lib/serafino/birth/$U"
for d in alles-zaehlt app-ausnahmen keine-pausen kinderstart statistik zuruecksetzen; do
    rm -rf "/var/lib/serafino/$d/$U" "/var/lib/serafino/$d/$U".* 2>/dev/null
done
rm -rf "/etc/serafino/pro-konto/$U" 2>/dev/null
rm -f "/var/lib/AccountsService/users/$U" "/var/lib/AccountsService/icons/$U"
rm -f /var/lib/timekpr/config/timekpr."$U".conf /var/lib/timekpr/work/"$U".* 2>/dev/null
rm -rf "/var/mail/$U" 2>/dev/null

# Hosts-Sperre aktualisieren (faellt weg, wenn kein Kind unter 13 mehr da ist)
/usr/local/bin/serafino-update-social-block.sh >/dev/null 2>&1
systemctl restart timekpr >/dev/null 2>&1 || systemctl restart timekprd >/dev/null 2>&1
exit 0
