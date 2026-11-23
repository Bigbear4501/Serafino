#!/bin/bash
#
# serafino-start-calamares.sh
#
# Zeigt zuerst einen Warnhinweis zur Festplatten-Formatierung an.
# Startet Calamares nur, wenn der Nutzer bestätigt. Benennt das
# Fenster im Hintergrund um, da der Fenstertitel "Calamares" fest im
# Programm steckt und nicht über die Branding-Konfiguration änderbar ist.

# Dialog-Fenster (kdialog, sonst zenity) mit Serafino-Logo
. /usr/local/lib/serafino/dialog.sh
if command -v kdialog >/dev/null 2>&1 || command -v zenity >/dev/null 2>&1; then
    # bz18: Ist auf dem Computer ein mit BitLocker verschlüsseltes Windows?
    # (Zum Ausprobieren ohne BitLocker: SERAFINO_BITLOCKER_TEST=1 serafino-start-calamares.sh)
    BL=$(lsblk -rno NAME,FSTYPE 2>/dev/null | awk '$2 == "BitLocker" {print "/dev/" $1}' | tr '\n' ' ')
    [ -n "${SERAFINO_BITLOCKER_TEST:-}" ] && BL="${BL:-/dev/TEST}"
    if [ -n "$BL" ]; then
        pd_frage "BitLocker gefunden – bitte zuerst lesen" "<b>Auf diesem Computer ist Windows mit BitLocker verschlüsselt</b> ($BL).\n\n<b>Du willst die ganze Festplatte löschen?</b> Dann brauchst du nichts weiter zu tun – Windows und BitLocker sind danach weg.\n\n<b>Du willst Serafino neben Windows installieren?</b> Dann bitte vorher in Windows:\n\n1. <b>Wiederherstellungsschlüssel aufschreiben</b> (48 Ziffern):\n    im Browser <b>aka.ms/myrecoverykey</b> öffnen und mit dem Microsoft-Konto anmelden.\n    Ohne diesen Schlüssel startet Windows nach der Installation womöglich nicht mehr.\n\n2. <b>Am besten BitLocker ausschalten:</b>\n    Windows-Suche → „BitLocker verwalten“ → „BitLocker deaktivieren“\n    (Windows Home: Einstellungen → Datenschutz und Sicherheit → Geräteverschlüsselung → Aus).\n    Warten, bis Windows fertig entschlüsselt hat – das kann eine Weile dauern.\n\nDanach Windows herunterfahren und wieder vom Serafino-Stick starten.\n\nMöchtest du trotzdem jetzt weitermachen?" "Weiter" "Abbrechen" || exit 0
    fi

    pd_frage "Achtung - Vor der Installation" "Bei der Installation von Serafino können Daten auf der Festplatte deines Computers gelöscht werden!\n\nBitte sichere wichtige Daten vorher an einem anderen Ort (z.B. USB-Stick).\n\nMöchtest du jetzt mit der Installation fortfahren?" "Ja, fortfahren" "Abbrechen"

    if [ $? -ne 0 ]; then
        # Abgebrochen - Installer nicht starten
        exit 0
    fi

    pd_info "Hinweis zum Benutzerkonto" "Auf der nächsten Seite legst du ein Benutzerkonto an.\n\nDieses erste Konto ist für ein Elternteil gedacht (mit vollen Rechten).\n\nEigene Konten für Kinder kannst du danach jederzeit im Eltern-Kontrollzentrum unter „Benutzerkonten“ anlegen." "Verstanden"
fi

# KDE-Aussehen: sudo setzt die Umgebung zurück, deshalb die KDE-Werte
# ausdrücklich mitgeben.
KDEENV=(QT_QPA_PLATFORMTHEME=kde XDG_CURRENT_DESKTOP=KDE KDE_FULL_SESSION=true
        LANG="${LANG:-de_DE.UTF-8}")

# Bug b22: Über XWayland kamen Zahlen und Sonderzeichen von der
# Bildschirmtastatur falsch an („1234“ wurde zu „!"§$“) – das Passwort aus
# dem Installer stimmte danach nicht. Darum Calamares unter Wayland direkt
# starten; die Bildschirmtastatur liefert dann echte Zeichen.
# Root darf den Wayland-Zugang des Live-Benutzers benutzen, wenn der Pfad
# vollständig angegeben ist. Klappt das nicht, geht es wie früher über XWayland.
start_wayland() {
    local sock="$WAYLAND_DISPLAY"
    [ -n "$sock" ] || return 1
    case "$sock" in /*) ;; *) sock="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}/$sock" ;; esac
    [ -S "$sock" ] || return 1
    sudo env "${KDEENV[@]}" QT_QPA_PLATFORM=wayland WAYLAND_DISPLAY="$sock" \
        XDG_RUNTIME_DIR=/run/user/0 calamares &
    CALAMARES_PID=$!
    # Stirbt Calamares in den ersten Sekunden, hat Wayland nicht geklappt.
    for _ in 1 2 3 4 5 6; do
        sleep 1
        kill -0 "$CALAMARES_PID" 2>/dev/null || { wait "$CALAMARES_PID"; [ $? -eq 0 ] && exit 0; return 1; }
    done
    return 0
}
start_xwayland() {
    sudo env "${KDEENV[@]}" DISPLAY="$DISPLAY" XAUTHORITY="${XAUTHORITY:-}" calamares &
    CALAMARES_PID=$!
}
sudo mkdir -p -m 700 /run/user/0 2>/dev/null
start_wayland || start_xwayland

# Im Hintergrund wiederholt versuchen, das Fenster umzubenennen,
# sobald es erscheint (kann ein paar Sekunden dauern, bis es da ist)
(
    for i in $(seq 1 30); do
        if command -v wmctrl &> /dev/null; then
            if wmctrl -l | grep -qi "calamares"; then
                wmctrl -r "Calamares" -N "Serafino installieren"
                break
            fi
        fi
        sleep 0.5
    done
) &

wait "$CALAMARES_PID"
