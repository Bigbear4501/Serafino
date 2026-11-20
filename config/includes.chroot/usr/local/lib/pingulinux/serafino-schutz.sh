#!/bin/sh
# serafino-schutz.sh – verhindert, dass apt oder Synaptic das Serafino-Paket entfernen
# (Kinderschutz, Kontrollzentrum, Fino). Läuft vor jedem dpkg-Aufruf
# (DPkg::Pre-Install-Pkgs, /etc/apt/apt.conf.d/10serafino-schutz) und bekommt von apt
# die Liste der geplanten Änderungen (Format VERSION 2).
#
# Wirklich entfernen (z. B. Serafino ganz loswerden):
#   sudo mkdir -p /etc/serafino && sudo touch /etc/serafino/entfernen-erlaubt
SCHUTZ="pingulinux-system"
NACHFOLGER="serafino-tools"      # Umbenennung in dann ist Entfernen erlaubt

[ -e /etc/serafino/entfernen-erlaubt ] && { cat >/dev/null; exit 0; }
IFS= read -r kopf || exit 0
case "$kopf" in "VERSION 2"*) ;; *) cat >/dev/null; exit 0 ;; esac
while IFS= read -r z; do [ -z "$z" ] && break; done     # Einstellungen überspringen

weg=""; nachfolger=""
while read -r pkg alt rich neu aktion; do
    [ "$pkg" = "$SCHUTZ" ] && [ "$aktion" = "**REMOVE**" ] && weg=1
    [ "$pkg" = "$NACHFOLGER" ] && [ "$aktion" != "**REMOVE**" ] && nachfolger=1
done
if [ -n "$weg" ] && [ -z "$nachfolger" ]; then
    echo "" >&2
    echo "Serafino: Das Paket $SCHUTZ (Kinderschutz, Kontrollzentrum, Fino) ist geschützt" >&2
    echo "und wird nicht entfernt. Es wurde nichts geändert." >&2
    echo "Wer Serafino wirklich entfernen will: sudo touch /etc/serafino/entfernen-erlaubt" >&2
    exit 1
fi
exit 0
