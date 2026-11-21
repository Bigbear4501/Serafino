#!/bin/sh
# ohne-passwort.sh – „Anmelden ohne Passwort“ für Kinderkonten absichern (bz21)
# Läuft beim Bauen (Hook 0570), bei jedem Start (serafino-ohne-passwort.service)
# und beim Anlegen/Umstellen eines Kontos (root-helper). Zwei unabhängige Wege:
#  1. PAM-Regel: Mitglieder der Gruppe nopasswdlogin brauchen am Anmeldebildschirm
#     (sddm) und an der Bildschirmsperre (kde) kein Passwort.
#  2. Das Konto selbst hat ein leeres Passwort – Debian erlaubt das (pam_unix nullok),
#     falls Weg 1 nicht greift. Dafür ist die Textkonsole (login) für diese Kinder
#     ganz gesperrt.
# Nur Kinderkonten (Alters-Profil, kein Admin) – alles andere bleibt unberührt.
LINE="auth    sufficient      pam_succeed_if.so user ingroup nopasswdlogin quiet"
getent group nopasswdlogin >/dev/null || groupadd -r nopasswdlogin
n=0
for f in /etc/pam.d/sddm /etc/pam.d/kde; do
    [ -f "$f" ] || continue
    if ! grep -q "ingroup nopasswdlogin" "$f"; then
        if grep -q '^@include common-auth' "$f"; then
            sed -i "0,/^@include common-auth/s||$LINE\n@include common-auth|" "$f"
        else
            sed -i "1a $LINE" "$f"
        fi
    fi
    grep -q "ingroup nopasswdlogin" "$f" && n=$((n+1))
done
# Textkonsole (Strg+Alt+F2 …): Kinder ohne Passwort dürfen sich dort NICHT anmelden –
# sonst käme man mit leerem Passwort an eine Kommandozeile.
SPERRE="auth    requisite       pam_succeed_if.so user notingroup nopasswdlogin quiet"
if [ -f /etc/pam.d/login ] && ! grep -q "notingroup nopasswdlogin" /etc/pam.d/login; then
    if head -1 /etc/pam.d/login | grep -q '^#%PAM'; then
        sed -i "1a $SPERRE" /etc/pam.d/login
    else
        sed -i "1i $SPERRE" /etc/pam.d/login
    fi
fi
konsole=$(grep -c "notingroup nopasswdlogin" /etc/pam.d/login 2>/dev/null)

# Weg 2: Mitglieder der Gruppe → leeres Passwort (nur Kinderkonten)
for u in $(getent group nopasswdlogin | cut -d: -f4 | tr ',' ' '); do
    [ -f "/var/lib/serafino/profiles/$u" ] || continue
    id -nG "$u" | tr ' ' '\n' | grep -qx sudo && continue
    [ -n "$(getent shadow "$u" | cut -d: -f2)" ] && passwd -d "$u" >/dev/null 2>&1
done
echo "OHNE-PASSWORT: Gruppe nopasswdlogin, PAM-Regel in $n Datei(en) (sddm, kde), Textkonsole gesperrt: ${konsole:-0}"
exit 0
