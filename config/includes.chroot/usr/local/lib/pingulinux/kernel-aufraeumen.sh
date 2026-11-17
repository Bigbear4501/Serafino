#!/bin/bash
# kernel-aufraeumen.sh – läuft beim Start, nachdem Eltern unter „Hardware &
# Treiber“ zurück auf den Debian-13-Kernel gewechselt haben. Läuft der
# Debian-13-Kernel, wird der Backports-Kernel entfernt und das Startmenü
# wieder normal eingestellt. Sonst bleibt alles, wie es ist (nächster Start).
MARK=/var/lib/pingulinux/kernel-aufraeumen
LOG=/var/log/pingulinux-treiber.log
[ -f "$MARK" ] || exit 0
exec >>"$LOG" 2>&1
echo "=== $(date '+%F %T') Kernel aufräumen (läuft: $(uname -r)) ==="
if dpkg-query -W -f='${Version}' "linux-image-$(uname -r)" 2>/dev/null | grep -q bpo; then
    echo "Läuft noch der Backports-Kernel – nichts entfernt."
    exit 0
fi
export DEBIAN_FRONTEND=noninteractive
P=$(dpkg-query -W -f='${Package} ${Version} ${Status}\n' 'linux-image-[0-9]*' 'linux-headers-[0-9]*' 'linux-kbuild-[0-9]*' 2>/dev/null \
    | awk '$2 ~ /bpo/ && /install ok installed/ {print $1}')
# shellcheck disable=SC2086
[ -n "$P" ] && apt-get -y purge $P
rm -f /etc/default/grub.d/50-pingulinux-kernel.cfg
update-grub
grub-set-default 0 2>/dev/null
rm -f "$MARK"
systemctl disable pingulinux-kernel-aufraeumen.service
echo "Fertig: $P entfernt."
