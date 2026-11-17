#!/bin/bash
#
# pingulinux-restzeit.sh  (be4) – läuft als root jede Minute (Timer)
#
# Schreibt für jedes Kinderkonto die Restzeit von heute nach
# /run/pingulinux/restzeit/BENUTZER  ("übrig_sek genutzt_sek").
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
    printf '%s %s\n' "$left" "$spent" > "$OUT/$u.tmp" && chmod 644 "$OUT/$u.tmp" && mv "$OUT/$u.tmp" "$OUT/$u"
done
exit 0
