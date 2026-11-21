#!/bin/bash
# serafino-age-from-birth.sh GEBURT  (Format JJJJ-MM-TT, ältere Konten: JJJJ-MM)
# Gibt das Alter in Jahren aus.
#  - Mit Tag: genau – ab dem Geburtstag zählt das neue Alter.
#  - Nur Monat (ältere Konten): vorsichtig gerechnet – im Geburtsmonat selbst
#    zählt das Kind noch als jünger, es wird erst im Folgemonat älter.
B="$1"
if [[ "$B" =~ ^([0-9]{4})-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$ ]]; then
    by=${BASH_REMATCH[1]}; bm=$((10#${BASH_REMATCH[2]})); bd=$((10#${BASH_REMATCH[3]}))
    y=$(date +%Y); m=$((10#$(date +%m))); d=$((10#$(date +%d)))
    age=$((y - by))
    if [ "$m" -lt "$bm" ] || { [ "$m" -eq "$bm" ] && [ "$d" -lt "$bd" ]; }; then
        age=$((age - 1))
    fi
elif [[ "$B" =~ ^([0-9]{4})-(0[1-9]|1[0-2])$ ]]; then
    by=${BASH_REMATCH[1]}; bm=$((10#${BASH_REMATCH[2]}))
    y=$(date +%Y); m=$((10#$(date +%m)))
    age=$((y - by))
    [ "$m" -le "$bm" ] && age=$((age - 1))
else
    exit 2
fi
[ "$age" -lt 0 ] && age=0
echo "$age"
