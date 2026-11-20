#!/bin/bash
#
# pingulinux-restzeit.sh  (be4) – läuft als root jede Minute (Timer)
#
# Schreibt für jedes Kinderkonto die Restzeit von heute nach
# /run/pingulinux/restzeit/BENUTZER  ("übrig_sek genutzt_sek zählt").
# „zählt“ (b29): 0 = die Zeit steht gerade, weil nur Programme laufen, die
# nicht zählen (Lernen, Malen …, Timekpr-PlayTime); 1 = sie läuft.
# Wird auch sofort nach „Mehr Zeit“ aufgerufen (Root-Helfer tk-extra).
# Der Startbildschirm der Kleinen zeigt daraus die untergehende Sonne
# (Timekpr gibt die Zeiten sonst nur mit Eltern-Rechten heraus).

command -v timekpra >/dev/null 2>&1 || exit 0
OUT=/run/pingulinux/restzeit
mkdir -p "$OUT"; chmod 755 /run/pingulinux "$OUT"
for f in /var/lib/pingulinux/profiles/*; do
    [ -f "$f" ] || continue
    u=$(basename "$f")
    id "$u" >/dev/null 2>&1 || continue
    info=$(timekpra --userinfo "$u" 2>/dev/null) || continue
    left=$(sed -nE 's/^\s*ACTUAL_TIME_LEFT_DAY\s*[:=]\s*(-?[0-9]+).*/\1/p' <<<"$info" | head -1)
    [ -n "$left" ] || left=$(sed -nE 's/^\s*TIME_LEFT_DAY\s*[:=]\s*(-?[0-9]+).*/\1/p' <<<"$info" | head -1)
    spent=$(sed -nE 's/^\s*ACTUAL_TIME_SPENT_DAY\s*[:=]\s*(-?[0-9]+).*/\1/p' <<<"$info" | head -1)
    [ -n "$spent" ] || spent=$(sed -nE 's/^\s*TIME_SPENT_DAY\s*[:=]\s*(-?[0-9]+).*/\1/p' <<<"$info" | head -1)
    [ -n "$left" ] && [ -n "$spent" ] || continue
    # Zählt die Zeit gerade? Nur wenn „Lernprogramme zählen nicht“ an ist und
    # kein Spiel/Video läuft, steht sie (PlayTime im Override-Modus).
    zaehlt=1
    wert() { sed -nE "s/^\s*$1\s*[:=]\s*(\S+).*/\1/p" <<<"$info" | head -1; }
    if [ ! -e "/var/lib/pingulinux/alles-zaehlt/$u" ] \
       && [ "$(wert PLAYTIME_ENABLED)" = True ] && [ "$(wert PLAYTIME_LIMIT_OVERRIDE_ENABLED)" = True ] \
       && [ "$(wert ACTUAL_ACTIVE_PLAYTIME_ACTIVITY_COUNT)" = 0 ]; then
        zaehlt=0
    fi
    printf '%s %s %s\n' "$left" "$spent" "$zaehlt" > "$OUT/$u.tmp" && chmod 644 "$OUT/$u.tmp" && mv "$OUT/$u.tmp" "$OUT/$u"
done
exit 0
