#!/bin/bash
#
# serafino-help.sh - Hilfe-Menue mit Verknuepfungen zu den Serafino-Seiten.
# Die Adressen stehen in /etc/serafino/links.conf (leer = noch in Arbeit).

. /usr/local/lib/serafino/dialog.sh
TITLE="Hilfe - Serafino"
source /etc/serafino/links.conf 2>/dev/null

open_link() {  # $1 Adresse, $2 Name
    if [ -z "$1" ]; then
        pd_info "$TITLE" "Die Seite „$2“ ist noch in Arbeit.\n\nSchau bald wieder vorbei!"
    else
        xdg-open "$1" >/dev/null 2>&1 &
    fi
}

while true; do
    CHOICE=$(pd_menue_ikon "$TITLE" "<big><b>Wie können wir helfen?</b></big>" \
        handbuch help-contents "Eltern-Handbuch (auch ohne Internet)" \
        einrichtung tools-wizard "Einrichtungs-Assistent (Kinder, Filter, Bildschirmzeit)" \
        faq help-about "Fragen von Eltern (Passwort vergessen, Sicherung …)" \
        ohnepw emblem-unlocked "Anmelden ohne Passwort (für die Kleinen)" \
        fino /usr/share/serafino/fino/fino.png "Überraschungen von Fino (zum Ausprobieren)" \
        pdf printer "Eltern-Handbuch als PDF (zum Ausdrucken)" \
        web internet-web-browser "Serafino-Webseite" \
        anleitung applications-education "Anleitungen" \
        community system-users "Fragen und Ideen (Forum für Eltern)" \
        fehler tools-report-bug "Fehler melden" \
        diagnose run-build "Fehlerdiagnose starten" \
        datenschutz security-high "Datenschutz" \
        impressum document-preview "Impressum" )

    case "$CHOICE" in
        handbuch) /usr/local/bin/serafino-handbuch.py 01-kontrollzentrum.md ;;
        einrichtung) /usr/local/bin/serafino-einrichtung.py ;;
        faq) /usr/local/bin/serafino-handbuch.py 02-eltern-faq.md ;;
        ohnepw) /usr/local/bin/serafino-handbuch.py 03-ohne-passwort.md ;;
        fino) /usr/local/bin/serafino-handbuch.py 04-ueberraschungen.md ;;
        pdf) xdg-open /usr/share/serafino/hilfe/Eltern-Handbuch.pdf >/dev/null 2>&1 & ;;
        web) open_link "$WEBSEITE" "Serafino-Webseite" ;;
        anleitung) if [ -n "$ANLEITUNGEN" ]; then open_link "$ANLEITUNGEN" "Anleitungen"; else /usr/local/bin/serafino-handbuch.py; fi ;;
        community) open_link "$COMMUNITY" "Community und Forum" ;;
        fehler) open_link "$FEHLER_MELDEN" "Fehler melden" ;;
        diagnose) /usr/local/bin/serafino-diagnose.sh ;;
        datenschutz) open_link "$DATENSCHUTZ" "Datenschutz" ;;
        impressum) open_link "$IMPRESSUM" "Impressum" ;;
        *) break ;;
    esac
done
