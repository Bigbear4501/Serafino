#!/bin/bash
#
# serafino-update-social-block.sh  (als root)
# Sperrt Social-Media-Seiten und normales YouTube pro Konto: Fuer jedes
# Kinderkonto unter 13 Jahren wird eine Markierungsdatei angelegt. Firefox
# (serafino.cfg) erkennt sie und setzt dann die feste Sperrliste
# /usr/share/serafino/block-social.pac. Eltern und aeltere Kinder sind
# nicht betroffen. Die frueheren Eintraege in /etc/hosts werden entfernt.

PROFDIR=/var/lib/serafino/profiles
MARKDIR=/var/lib/serafino/blocksocial

mkdir -p "$MARKDIR"
chmod 755 "$MARKDIR"

# Alte systemweite Sperre aus /etc/hosts entfernen
sed -i '/^# BEGIN serafino-social$/,/^# END serafino-social$/d' /etc/hosts
sed -i '/^# BEGIN serafino-youtube$/,/^# END serafino-youtube$/d' /etc/hosts

# Alle Markierungen neu setzen
rm -f "$MARKDIR"/* 2>/dev/null
for f in "$PROFDIR"/*; do
  [ -f "$f" ] || continue
  u=$(basename "$f")
  id "$u" >/dev/null 2>&1 || { rm -f "$f"; continue; }   # geloeschte Konten
  a=$(cat "$f")
  if [ "$a" -lt 13 ] 2>/dev/null; then
    : > "$MARKDIR/$u"
    chmod 644 "$MARKDIR/$u"
  fi
done
exit 0
