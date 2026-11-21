#!/bin/sh
# serafino-virenscanner.sh install|remove   (läuft als root, aufgerufen vom App Store)
# ClamUI (Flatpak) ist nur die Oberfläche – die eigentliche Prüfung macht ClamAV
# aus Debian (clamscan). Ohne Hintergrunddienst: kein clamav-daemon, und der
# freshclam-Dienst wird abgeschaltet. Neue Virendaten gibt es nur, wenn die
# Eltern ClamUI öffnen und dort aktualisieren (beim Installieren einmal gleich).
set -u
export DEBIAN_FRONTEND=noninteractive
case "${1:-}" in
install)
    # freshclam soll nicht als Dienst laufen ("manual" statt "daemon")
    echo "clamav-freshclam clamav-freshclam/autoupdate_freshclam select manual" | debconf-set-selections
    apt-get update -qq
    apt-get install -y --no-install-recommends clamav || exit 1
    systemctl disable --now clamav-freshclam.service 2>/dev/null
    systemctl mask clamav-freshclam.service 2>/dev/null
    echo "Virendaten werden geladen (beim ersten Mal etwa 200 MB) …"
    freshclam --quiet || echo "Virendaten konnten nicht geladen werden – später in ClamUI erneut versuchen."
    exit 0 ;;
remove)
    apt-get purge -y --no-auto-remove clamav clamav-freshclam
    rc=$?
    systemctl unmask clamav-freshclam.service 2>/dev/null
    exit $rc ;;
*)
    echo "Aufruf: $0 install|remove" >&2; exit 2 ;;
esac
