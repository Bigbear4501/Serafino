#!/bin/bash
#
# serafino-aufraeumen.sh (bz33/bz34) – läuft als root, einmal pro Woche per Timer
#
# Räumt das System nach den automatischen Updates auf:
#   - Programmteile, die nicht mehr gebraucht werden (apt autoremove),
#     dazu alte Kernel – der laufende und der vorherige bleiben immer
#   - Download-Zwischenspeicher von apt (/var/cache/apt/archives)
#   - Flatpak-Reste (Laufzeiten, die kein Programm mehr braucht)
#
# Sicherheit (Lehre aus dem Plymouth-Bug b27):
#   - Beim ersten Lauf wird alles, was gerade installiert ist, als „gewollt“
#     markiert (apt-mark manual) – außer Kernel und Installer-Teilen. Entfernt
#     wird danach nur, was durch spätere Updates oder Deinstallationen übrig bleibt.
#   - Vorher Probelauf: Steht etwas Wichtiges auf der Liste, oder sind es mehr
#     als 30 Pakete, wird NICHTS entfernt und der Grund ins Protokoll geschrieben.
#
# Ausschalten: sudo touch /etc/serafino/kein-aufraeumen
# Protokoll:   /var/log/serafino/aufraeumen.log

grep -qw boot=live /proc/cmdline 2>/dev/null && exit 0
[ -e /etc/serafino/kein-aufraeumen ] && exit 0
# Kernel-Wechsel (Hardware & Treiber) noch nicht abgeschlossen → nächste Woche
[ -e /var/lib/serafino/kernel-aufraeumen ] && exit 0

mkdir -p /var/log/serafino /var/lib/serafino
LOG=/var/log/serafino/aufraeumen.log
MARK=/var/lib/serafino/.pakete-verankert
exec >>"$LOG" 2>&1
echo "=== $(date '+%d.%m.%Y %H:%M') ==="
export DEBIAN_FRONTEND=noninteractive
APT=(apt-get -q -o DPkg::Lock::Timeout=900)
KERNEL='^linux-(image|headers|modules|kbuild)-[0-9]'
# Darf nie automatisch entfernt werden (Sicherheitsbremse)
WICHTIG='^(serafino-tools|pingulinux-system|kde-plasma-desktop|plasma-desktop|plasma-workspace|kwin-wayland|sddm|plymouth|plymouth-themes|firefox-esr|network-manager|timekpr-next|flatpak|timeshift|ufw|cups|sane-utils|grub-efi-amd64|grub-efi-amd64-signed|grub-pc|shim-signed|systemd|sudo|polkitd|pkexec|unattended-upgrades|apt|dpkg|linux-image-amd64|fonts-noto-color-emoji|konsole|dolphin|calamares-settings-serafino)$'
# Läuft gerade apt, dpkg, Synaptic oder ein automatisches Update? Dann warten
# (höchstens 30 Minuten), sonst nächstes Mal.
for i in $(seq 1 60); do
    pgrep -x 'apt|apt-get|dpkg|aptitude|synaptic|unattended-upgr' >/dev/null || break
    [ "$i" = 60 ] && { echo "apt läuft seit 30 Minuten – heute nicht aufgeräumt."; exit 0; }
    sleep 30
done
vorher=$(df --output=avail -k / | tail -1)

# 1. Verankern (bz34) – einmal pro Rechner
if [ ! -e "$MARK" ]; then
    liste=$(dpkg-query -W -f='${db:Status-Abbrev} ${binary:Package}\n' \
            | awk '$1 == "ii" {print $2}' \
            | grep -Ev "$KERNEL" \
            | grep -Ev '^(calamares|live-boot|live-config|live-tools|live-task|user-setup)')
    if [ -n "$liste" ] && echo "$liste" | xargs -r apt-mark manual >/dev/null; then
        touch "$MARK"
        echo "Verankert: $(echo "$liste" | wc -l) installierte Pakete gelten als gewollt."
    else
        echo "STOPP: Verankern hat nicht geklappt – heute wird nichts entfernt."
        exit 0
    fi
fi

# 2. Probelauf: Was würde entfernt?
weg=$("${APT[@]}" -s autoremove 2>/dev/null | awk '/^Remv /{print $2}')
andere=$(echo "$weg" | grep -Ev "$KERNEL" | grep -v '^$')
anzahl=$(echo "$andere" | grep -c . )
stopp=""
if echo "$weg" | grep -qx "linux-image-$(uname -r)"; then
    stopp="laufender Kernel stünde auf der Liste"
elif treffer=$(echo "$andere" | grep -E "$WICHTIG"); then
    stopp="wichtige Pakete stünden auf der Liste: $(echo $treffer)"
elif [ "$anzahl" -gt 30 ]; then
    stopp="$anzahl Pakete auf einmal – zu viele, bitte von Hand prüfen (sudo apt autoremove --dry-run)"
fi

# 3. Entfernen
if [ -n "$stopp" ]; then
    echo "STOPP, nichts entfernt: $stopp"
elif [ -n "$weg" ]; then
    echo "Entferne: $(echo $weg)"
    "${APT[@]}" -y autoremove
    echo "apt autoremove rc=$?"
else
    echo "Nichts zu entfernen."
fi

# 4. Download-Zwischenspeicher leeren
"${APT[@]}" clean && echo "Download-Zwischenspeicher geleert."

# 5. Flatpak-Reste
if command -v flatpak >/dev/null 2>&1; then
    nice -n 19 flatpak uninstall --system --unused -y --noninteractive
    echo "flatpak uninstall --unused rc=$?"
fi

nachher=$(df --output=avail -k / | tail -1)
echo "Frei geworden: $(( (nachher - vorher) / 1024 )) MB"
date '+%d.%m.%Y %H:%M' > /var/lib/serafino/aufraeumen-zuletzt
exit 0
