#!/bin/bash
#
# serafino-create-restricted-user.sh
#
# Läuft mit erhöhten Rechten (über pkexec aufgerufen). Legt einen
# NICHT-Admin-Benutzer an (keine sudo-Gruppe) und sperrt zusätzlich
# den Zugriff auf den Terminal-Emulator für genau dieses Konto
# (über eine Zugriffsrechte-Regel/ACL, andere Konten bleiben
# unberührt).
#
# Aufruf: USERNAME als $1, Passwort wird über stdin eingelesen.

set -e

USERNAME="$1"
AGE="$2"   # Geburtsmonat JJJJ-MM (oder Alter in Jahren)
AVATAR="$3"
ANZEIGE="$4"   # Anzeigename (Gross-/Kleinschreibung), leer = wie Anmeldename
PASSWORD=$(cat)

OPTS=()
[ -n "$ANZEIGE" ] && OPTS=(-c "$ANZEIGE")
useradd -m -s /bin/bash "${OPTS[@]}" "$USERNAME"
echo "${USERNAME}:${PASSWORD}" | chpasswd

# Kinder-Konten sollen das Eltern-Kontrollzentrum nicht automatisch
# oeffnen (nur Admin-/Eltern-Konten bekommen den Autostart).
rm -f "/home/${USERNAME}/.config/autostart/serafino-parental-control.desktop" \
      "/home/${USERNAME}/Desktop/serafino-parental-control.desktop"

# Terminal-Zugriff für genau dieses Konto sperren (kein Admin-Konto
# betroffen, nur dieses neue). Erfordert das Paket "acl".
if command -v setfacl &> /dev/null; then
    setfacl -m u:"${USERNAME}":--- /usr/bin/konsole 2>/dev/null || true
    setfacl -m u:"${USERNAME}":--- /usr/bin/konsole 2>/dev/null || true
fi

# YouTube Kids als Symbol auf dem Desktop des Kindes
mkdir -p "/home/${USERNAME}/Desktop"
ln -sfn /usr/share/applications/serafino-youtube-kids.desktop "/home/${USERNAME}/Desktop/serafino-youtube-kids.desktop"
chown -R "${USERNAME}:${USERNAME}" "/home/${USERNAME}/Desktop" 2>/dev/null || true

# Alters-Profil (Bildschirmzeit, Social-Media-Sperre) automatisch setzen
if [ -n "$AGE" ]; then
    case "$AGE" in
        *-*)
            mkdir -p /var/lib/serafino/birth
            echo "$AGE" > "/var/lib/serafino/birth/$USERNAME"
            AGE=$(/usr/local/bin/serafino-age-from-birth.sh "$AGE") || AGE=""
            ;;
    esac
    [ -n "$AGE" ] && /usr/local/bin/serafino-apply-age-profile.sh "$USERNAME" "$AGE" || true
fi

# Profilbild (leer = Fino-Standardbild bleibt)
if [ -n "$AVATAR" ] && [ -f "$AVATAR" ]; then
    /usr/local/bin/serafino-set-avatar.sh "$USERNAME" "$AVATAR" || true
fi
