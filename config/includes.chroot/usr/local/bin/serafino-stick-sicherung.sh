#!/bin/bash
#
# serafino-stick-sicherung.sh – automatische Sicherung der eigenen Dateien
# auf den Sicherungs-Stick (z4). Läuft als root.
#
#   serafino-stick-sicherung.sh UUID     beim Einstecken (udev → systemd)
#   serafino-stick-sicherung.sh --alle   regelmäßig (Timer), solange er steckt
#
# Welche Sticks? Die, auf die schon einmal von Hand gesichert wurde
# (Kontrollzentrum → Sicherung → „Auf USB-Stick sichern“, eigene Dateien).
# Sie stehen in /var/lib/pingulinux/sicherungs-sticks.
#
# Gesichert werden nur die eigenen Dateien (wie von Hand, nichts wird auf dem
# Stick gelöscht). Die System-Sicherung bleibt Handarbeit.
#
#   beim Einstecken: wenn die letzte Sicherung älter als 1 Stunde ist
#   steckt er:       alle 4 Stunden
#
# Eltern bekommen eine kurze Meldung (Anfang und Ende).

LISTE=/var/lib/pingulinux/sicherungs-sticks
LETZTE=/var/lib/pingulinux/stick-letzte
WORKER=/usr/local/bin/pingulinux-sicherung-usb-worker.sh
RESULT=/var/lib/pingulinux/usb-sicherung-ergebnis
MNT=/run/serafino/stick-sicherung
LOG=/var/log/pingulinux-sicherung-usb.log

grep -qw boot=live /proc/cmdline 2>/dev/null && exit 0
[ -s "$LISTE" ] || exit 0

exec 9>/run/serafino-stick-sicherung.lock
flock -n 9 || exit 0

# Kurze Meldung an angemeldete Eltern (nicht an Kinder)
melden() {
    local titel="$1" text="$2"
    loginctl list-sessions --no-legend 2>/dev/null | while read -r sid uid user _; do
        [ -n "$uid" ] || continue
        [ "$(loginctl show-session "$sid" -p Active --value 2>/dev/null)" = yes ] || continue
        case "$(loginctl show-session "$sid" -p Type --value 2>/dev/null)" in wayland|x11) ;; *) continue ;; esac
        id -nG "$user" 2>/dev/null | tr ' ' '\n' | grep -qx sudo || continue
        bus="unix:path=/run/user/$uid/bus"
        if command -v notify-send >/dev/null; then
            runuser -u "$user" -- env DBUS_SESSION_BUS_ADDRESS="$bus" \
                notify-send -a Serafino -i drive-removable-media-usb "$titel" "$text" 2>/dev/null
        else
            runuser -u "$user" -- env DBUS_SESSION_BUS_ADDRESS="$bus" gdbus call --session \
                --dest org.freedesktop.Notifications --object-path /org/freedesktop/Notifications \
                --method org.freedesktop.Notifications.Notify Serafino 0 drive-removable-media-usb \
                "$titel" "$text" '[]' '{}' 8000 >/dev/null 2>&1
        fi
    done
}

sichern() {     # UUID MINDESTABSTAND_SEKUNDEN
    local U="$1" ABSTAND="$2" DEV LABEL MP MEINS= ALT
    grep -q "^$U"$'\t' "$LISTE" || return 0
    DEV=$(readlink -f "/dev/disk/by-uuid/$U" 2>/dev/null)
    [ -b "$DEV" ] || return 0
    ALT=$(stat -c %Y "$LETZTE/$U" 2>/dev/null || echo 0)
    [ $(( $(date +%s) - ALT )) -ge "$ABSTAND" ] || return 0
    LABEL=$(awk -F'\t' -v u="$U" '$1==u {print $2}' "$LISTE")

    MP=$(findmnt -rn -S "$DEV" -o TARGET 2>/dev/null | head -1)
    if [ -z "$MP" ]; then
        mkdir -p "$MNT"
        mount -o noatime "$DEV" "$MNT" 2>>"$LOG" || return 0
        MP="$MNT"; MEINS=1
    fi
    echo "$(date '+%F %T') automatische Stick-Sicherung: $LABEL ($DEV)" >>"$LOG"
    melden "Sicherung auf den Stick" "Eigene Dateien werden auf „$LABEL“ gesichert – Stick bitte stecken lassen."
    "$WORKER" sichern "$DEV" "$MP" daten >/dev/null 2>&1
    sync
    if grep -q "^✓" "$RESULT" 2>/dev/null && ! grep -q "^✗" "$RESULT"; then
        mkdir -p "$LETZTE"; touch "$LETZTE/$U"
        melden "Sicherung auf den Stick" "Fertig ✓ Eigene Dateien sind auf „$LABEL“ gesichert."
    else
        melden "Sicherung auf den Stick" "Hat nicht geklappt: $(head -1 "$RESULT" 2>/dev/null | sed 's/^✗ //')"
    fi
    [ -n "$MEINS" ] && umount "$MNT" 2>/dev/null
    return 0
}

if [ "${1:-}" = --alle ]; then
    while IFS=$'\t' read -r U _; do
        [ -n "$U" ] && sichern "$U" $((4 * 3600))
    done < "$LISTE"
elif [[ "${1:-}" =~ ^[A-Za-z0-9-]+$ ]]; then
    sleep 8                      # Stick fertig erkennen lassen (und Desktop einbinden)
    sichern "$1" 3600
fi
exit 0
