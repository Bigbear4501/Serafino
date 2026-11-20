#!/bin/bash
# serafino-wlan-alle.sh (be4o) – WLAN der Eltern gilt für alle Kinderkonten
#
# Läuft im Eltern-Konto (Autostart) und schaut nach, sobald sich am Netzwerk etwas
# ändert. Jedes WLAN, das nur für dieses Eltern-Konto gespeichert ist (KDE fragt
# sonst das Passwort aus der KDE-Brieftasche ab), wird für alle Benutzer verfügbar
# gemacht: Das WLAN-Passwort wandert in die Systemeinstellung von NetworkManager
# (/etc/NetworkManager/system-connections, nur für root lesbar). Kinder verbinden
# sich dann von selbst, kennen das Passwort aber nicht und können es nicht anzeigen
# (Polkit-Regel 10-serafino-wlan.rules).
#
# Das Passwort geht nur über stdin an den Root-Teil, nie über die Befehlszeile
# (die könnte jedes Konto mit ps sehen). Es wird nirgends protokolliert.
#
# Aufruf:  serafino-wlan-alle.sh          einmal alle WLANs prüfen
#          serafino-wlan-alle.sh --wache  prüfen und bei Netzwerk-Änderungen erneut
set -u
export LC_ALL=C

id -nG 2>/dev/null | tr ' ' '\n' | grep -qx sudo || exit 0       # nur Eltern (Admins)
[ -f "/var/lib/pingulinux/profiles/$(id -un)" ] && exit 0        # nie in Kinderkonten
command -v nmcli >/dev/null 2>&1 || exit 0
ROOT=/usr/local/lib/pingulinux/serafino-wlan-alle-root.py
[ -x "$ROOT" ] || exit 0
LOG="$HOME/.local/state/serafino/wlan-alle.log"
mkdir -p "${LOG%/*}" 2>/dev/null

log() { printf '%s %s\n' "$(date '+%F %T')" "$*" >> "$LOG" 2>/dev/null; }

# nmcli -g maskiert „:“ und „\“ mit einem Backslash – zurückverwandeln
roh() { sed 's/\\\(.\)/\1/g'; }

feld() { nmcli -g "$1" connection show uuid "$2" 2>/dev/null | roh; }

einmal() {
    local uuid typ name perm km flags psk
    while IFS= read -r zeile; do
        uuid=${zeile%%:*}; typ=${zeile#*:}
        [ "$typ" = 802-11-wireless ] || continue
        name=$(feld connection.id "$uuid")
        perm=$(feld connection.permissions "$uuid")
        km=$(feld 802-11-wireless-security.key-mgmt "$uuid")
        flags=$(feld 802-11-wireless-security.psk-flags "$uuid")
        case "$km" in
            ""|owe)                                   # offenes WLAN: nur freigeben
                [ -z "$perm" ] && continue
                psk="" ;;
            wpa-psk|sae)
                if [ -z "$perm" ] && [[ "$flags" =~ ^(0|none) ]]; then continue; fi  # schon für alle
                psk=""
                if ! [[ "$flags" =~ ^(0|none) ]]; then
                    # Passwort liegt in der KDE-Brieftasche – NetworkManager fragt sie für uns
                    psk=$(nmcli -s -g 802-11-wireless-security.psk connection show uuid "$uuid" 2>/dev/null | roh)
                    if [ -z "$psk" ]; then
                        log "„$name“: Passwort (noch) nicht lesbar – Brieftasche gesperrt? Später nochmal."
                        continue
                    fi
                fi ;;
            *)                                        # WEP, Firmen-WLAN (802.1X): nicht anfassen
                [ -n "$perm" ] && log "„$name“: Art $km wird nicht automatisch freigegeben."
                continue ;;
        esac
        if printf '%s\n' "$psk" | pkexec "$ROOT" "$uuid" >>"$LOG" 2>&1; then
            log "„$name“ gilt jetzt für alle Konten."
        else
            log "„$name“: Freigeben hat nicht geklappt."
        fi
        psk=""
    done < <(nmcli -t -f UUID,TYPE connection show 2>/dev/null)
}

einmal
[ "${1:-}" = "--wache" ] || exit 0

# Später nochmal (Brieftasche ist beim Anmelden evtl. noch zu), dann bei jeder Änderung
( sleep 60; einmal ) &
letzt=0
nmcli monitor 2>/dev/null | while IFS= read -r z; do
    case "$z" in
        *": connected"*|*"is now the primary connection"*|*"connection profile"*|*"Connection "*) ;;
        *) continue ;;
    esac
    jetzt=$(date +%s)
    [ $((jetzt - letzt)) -lt 10 ] && continue
    letzt=$jetzt
    sleep 3
    einmal
done
