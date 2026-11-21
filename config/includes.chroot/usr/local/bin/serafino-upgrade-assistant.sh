#!/bin/bash
#
# serafino-upgrade-assistant.sh
# Update-Assistent: normale Updates und Wechsel auf eine neue Debian-Version.

. /usr/local/lib/serafino/dialog.sh
TITLE="Update-Assistent"

if grep -q "boot=live" /proc/cmdline 2>/dev/null; then
    pd_info "$TITLE" "Im Live-Modus läuft Serafino nur im Arbeitsspeicher.\n\nUpdates und ein Versionswechsel sind erst nach der Installation auf die Festplatte möglich."
    exit 0
fi

number() { case "$1" in bookworm) echo 12;; trixie) echo 13;; forky) echo 14;; duke) echo 15;; *) echo "$1";; esac; }

run_with_progress() {  # $1 Text, Rest: Befehl
    local text="$1"; shift
    pd_warten "$TITLE" "$text" "$@"
}

CHOICE=$(pd_menue_ikon "$TITLE" "<big><b>Was möchtest du tun?</b></big>" \
    updates system-software-update "Updates installieren (gleiche Debian-Version)" \
    wechsel system-upgrade "Auf neue Debian-Version wechseln")
[ -z "$CHOICE" ] && exit 0

case "$CHOICE" in
updates)
    pd_frage "$TITLE" "Alle verfügbaren Updates werden jetzt installiert.\nDas kann einige Minuten dauern. Bitte Gerät am Strom lassen." "Starten" "Abbrechen" || exit 0
    if run_with_progress "Updates werden installiert…" pkexec /usr/local/bin/serafino-update-worker.sh; then
        pd_info "$TITLE" "Alles ist auf dem neuesten Stand."
    else
        pd_fehler_roh "$TITLE" "Beim Aktualisieren ist ein Fehler aufgetreten.

Die letzten Zeilen des Protokolls (/var/log/serafino-update.log):

$(tail -n 8 /var/log/serafino-update.log 2>/dev/null)"
    fi
    ;;
wechsel)
    CUR=$(. /etc/os-release; echo "$VERSION_CODENAME")
    NEWC=$(curl -fsS -m 15 https://deb.debian.org/debian/dists/stable/Release 2>/dev/null | sed -n 's/^Codename: //p' | head -1)
    if [ -z "$NEWC" ]; then
        pd_fehler "$TITLE" "Ich konnte nicht prüfen, ob es eine neue Debian-Version gibt.\nBitte prüfe die Internetverbindung."
        exit 1
    fi
    if [ "$NEWC" = "$CUR" ]; then
        pd_info "$TITLE" "Du hast schon die neueste Debian-Version: <b>Debian $(number "$CUR") ($CUR)</b>.\n\nNormale Updates bekommst du über „Updates installieren“."
        exit 0
    fi
    pd_frage "$TITLE" "Es gibt eine neue Debian-Version:\n\n<b>Debian $(number "$CUR") ($CUR)  →  Debian $(number "$NEWC") ($NEWC)</b>\n\nDer Wechsel dauert 30 bis 90 Minuten.\n• Das Gerät muss am Strom bleiben.\n• Die Internetverbindung muss durchgehend bestehen.\n• Vorher wird eine Sicherung (Timeshift) erstellt.\n\nMöchtest du fortfahren?" "Ja, weiter" "Abbrechen" || exit 0

    MODE=backup
    run_with_progress "Sicherung und Wechsel auf Debian $(number "$NEWC")… Bitte nicht ausschalten!" pkexec /usr/local/bin/serafino-upgrade-worker.sh "$CUR" "$NEWC" backup
    RC=$?
    if [ "$RC" = 20 ]; then
        if pd_frage "$TITLE" "Die Sicherung konnte nicht erstellt werden.\n\nTipp: Richte zuerst unter „Sicherung und Wiederherstellung“ Timeshift ein.\n\nOhne Sicherung fortzufahren ist riskant. Wirklich weitermachen?" "Trotzdem fortfahren" "Abbrechen"; then
            run_with_progress "Debian $(number "$NEWC") wird installiert… Bitte nicht ausschalten!" pkexec /usr/local/bin/serafino-upgrade-worker.sh "$CUR" "$NEWC" nobackup
            RC=$?
        else
            exit 0
        fi
    fi

    if [ "$RC" = 0 ]; then
        pd_frage "$TITLE" "Fertig! Serafino läuft jetzt auf Debian $(number "$NEWC").\n\nBitte starte den Computer neu." "Jetzt neu starten" "Später" && systemctl reboot
    else
        pd_fehler_roh "$TITLE" "Der Wechsel ist fehlgeschlagen.

Deine alten Paketquellen wurden – wenn möglich – wiederhergestellt.
Du kannst über „Sicherung und Wiederherstellung“ den alten Stand zurückholen.

Die letzten Zeilen des Protokolls (/var/log/serafino-upgrade.log):

$(tail -n 8 /var/log/serafino-upgrade.log 2>/dev/null)"
    fi
    ;;
esac
