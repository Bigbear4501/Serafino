#!/bin/bash
#
# serafino-parental-control.sh
#
# Eltern-Kontrollzentrum: passwortgeschütztes Menü, das die
# wichtigsten Verwaltungswerkzeuge bündelt.

# --- Passwort-Abfrage (sudo-Passwort des Nutzers) ---
# Dialog-Fenster (kdialog, sonst zenity) mit Serafino-Logo
. /usr/local/lib/serafino/dialog.sh
# Im Live-Modus gibt es keine Passwort-Abfrage (Testsystem, Sudo ohne Passwort).
# Auf dem installierten System wird das Administrator-Passwort geprueft.
if ! grep -q "boot=live" /proc/cmdline 2>/dev/null; then
    sudo -k  # bisherigen sudo-Cache verwerfen, damit wirklich neu geprüft wird

    PASSWORD=$(pd_passwort "Eltern-Kontrollzentrum" "Passwort eines Erwachsenen:")
    if [ -z "$PASSWORD" ]; then
        exit 0
    fi

    if ! echo "$PASSWORD" | sudo -S true 2>/dev/null; then
        pd_fehler "Eltern-Kontrollzentrum" "Das Passwort stimmt nicht. Bitte versuche es noch einmal."
        exit 1
    fi
fi

# --- Hauptmenü als Kacheln ---
if [ -x /usr/local/bin/serafino-control-tiles.py ] && /usr/bin/python3 -c "import PyQt6.QtWidgets" 2>/dev/null; then
    exec /usr/local/bin/serafino-control-tiles.py
fi

# Ersatz (Liste), falls die Kachel-Ansicht nicht startet
while true; do
    # Ersatz-Menü: Schlüssel = angezeigter Text, damit die Fälle unten gleich bleiben
    ITEMS=("Bildschirmzeit" "Firewall und Netzwerk" "Kinderschutz-Filter ein/aus"
           "Drucker und Scanner" "Sicherung und Wiederherstellung" "Benutzerkonten"
           "Konten-Übersicht" "Serafino App Store" "Update-Assistent (neue Debian-Version)"
           "Systembereinigung" "Hilfe und Fehlerdiagnose" "Hilfe")
    ARGS=(); for i in "${ITEMS[@]}"; do ARGS+=("$i" "$i"); done
    CHOICE=$(pd_menue "Eltern-Kontrollzentrum" "<big><b>Hallo! Was möchtest du verwalten?</b></big>" "${ARGS[@]}")

    case "$CHOICE" in
        "Bildschirmzeit")
            /usr/local/bin/serafino-admin-tool.sh bildschirmzeit &
            ;;
        "Firewall und Netzwerk")
            /usr/local/bin/serafino-admin-tool.sh firewall &
            ;;
        "Kinderschutz-Filter ein/aus")
            /usr/local/bin/serafino-toggle-dns-filter.sh
            ;;
        "Drucker und Scanner")
            kcmshell6 kcm_printer_manager &
            ;;
        "Sicherung und Wiederherstellung")
            /usr/local/bin/serafino-admin-tool.sh sicherung &
            ;;
        "Benutzerkonten")
            /usr/local/bin/serafino-manage-users.sh &
            ;;
        "Konten-Übersicht")
            /usr/local/bin/serafino-admin-tool.sh konten &
            ;;
        "Update-Assistent (neue Debian-Version)")
            /usr/local/bin/serafino-upgrade-assistant.sh
            ;;
        "Systembereinigung")
            /usr/local/bin/serafino-cleanup.sh
            ;;
        "Hilfe und Fehlerdiagnose")
            /usr/local/bin/serafino-diagnose.sh
            ;;
        "Serafino App Store")
            /usr/local/bin/serafino-store.py &
            ;;
        "Hilfe")
            /usr/local/bin/serafino-help.sh
            ;;
        *)
            break
            ;;
    esac
done
