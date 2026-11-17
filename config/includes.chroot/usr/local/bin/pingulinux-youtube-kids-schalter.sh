#!/bin/bash
#
# pingulinux-youtube-kids-schalter.sh  (be9)
# Kontrollzentrum → „YouTube Kids“: Dürfen Kinder YouTube Kids selbst starten,
# oder nur mit dem Eltern-Passwort? Gilt für alle Kinderkonten.
. /usr/local/lib/pingulinux/dialog.sh
TITEL="YouTube Kids"
MIT=/var/lib/pingulinux/youtube-kids-mit-passwort

if [ -e "$MIT" ]; then frei=aus; pw=an; jetzt="nur mit Eltern-Passwort"
else frei=an; pw=aus; jetzt="Kinder starten es selbst"; fi

WAHL=$(pd_radio "$TITEL" "<b>Wie dürfen Kinder YouTube Kids öffnen?</b>\n\nJetzt: <b>$jetzt</b>\n\nIn YouTube Kids sind nur Kinder-Videos zu sehen, andere Seiten sind gesperrt.\nMit Passwort schaut ihr gemeinsam: Ein Erwachsener gibt beim Öffnen das Passwort ein." \
    frei "Kinder starten YouTube Kids selbst" "$frei" \
    pw "Nur mit Eltern-Passwort (gemeinsam schauen)" "$pw") || exit 0

case "$WAHL" in
    frei) [ -e "$MIT" ] || exit 0; ZIEL=aus; TEXT="Kinder können YouTube Kids jetzt selbst öffnen." ;;
    pw)   [ -e "$MIT" ] && exit 0; ZIEL=an;  TEXT="YouTube Kids braucht ab jetzt das Eltern-Passwort." ;;
    *)    exit 0 ;;
esac
pkexec /usr/local/bin/pingulinux-root-helper yt-pw "$ZIEL"
RC=$?
if [ $RC -eq 0 ]; then
    pd_info "$TITEL" "$TEXT"
elif [ $RC -ne 126 ] && [ $RC -ne 127 ]; then
    pd_fehler "$TITEL" "Das hat nicht geklappt."
fi
