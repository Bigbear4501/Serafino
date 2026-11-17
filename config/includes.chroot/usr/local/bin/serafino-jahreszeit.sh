#!/bin/bash
#
# serafino-jahreszeit.sh – Fino durchs Jahr (bz13)
#
# Wechselt beim Anmelden den Schreibtisch-Hintergrund passend zur Jahreszeit:
#   Dezember–Februar  Winter   (Schneemann, Schal)
#   März–Mai          Ostern   (Eier, Hase, Blumen)
#   Juni–August       Sommer   (Strand, Sonnenbrille)
#   September–November Herbst  (Drachen, Laub, Kürbisse)
#
# Nur wenn der Hintergrund noch einer von Serafino ist – wer selbst ein
# anderes Bild gewählt hat, behält es. Aus für alle: Datei
# /etc/serafino/keine-jahreszeiten anlegen.

[ -e /etc/serafino/keine-jahreszeiten ] && exit 0
DIR=/usr/share/backgrounds/pingulinux
case "$(date +%m)" in
    12|01|02) BILD=winter ;;
    03|04|05) BILD=ostern ;;
    06|07|08) BILD=sommer ;;
    *)        BILD=herbst ;;
esac
ZIEL="$DIR/serafino-$BILD.png"
[ -f "$ZIEL" ] || exit 0

# Plasma muss bereit sein
for i in $(seq 1 30); do
    dbus-send --session --print-reply --dest=org.kde.plasmashell /PlasmaShell \
        org.freedesktop.DBus.Introspectable.Introspect >/dev/null 2>&1 && break
    sleep 1
done
sleep 5     # Ersteinrichtung (pingulinux-plasma-first-run.sh) zuerst

RC="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"
JETZT=$(grep -h '^Image=' "$RC" 2>/dev/null | head -1 | sed 's/^Image=//; s|^file://||')
case "$JETZT" in
    ""|"$DIR"/wallpaper.png|"$DIR"/serafino-*.png) ;;     # unser Bild (oder noch keins)
    *) exit 0 ;;                                           # selbst gewählt – nichts ändern
esac
[ "$JETZT" = "$ZIEL" ] && exit 0
command -v plasma-apply-wallpaperimage >/dev/null && plasma-apply-wallpaperimage "$ZIEL" >/dev/null 2>&1
exit 0
