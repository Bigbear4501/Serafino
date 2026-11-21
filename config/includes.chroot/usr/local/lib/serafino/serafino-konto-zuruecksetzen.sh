#!/bin/bash
#
# serafino-konto-zuruecksetzen.sh KIND   (als root, über den Root-Helfer)  – bz8
#
# Setzt ein Kinderkonto auf Anfang: Einstellungen aller Programme und der
# Schreibtisch sind danach wie bei einem neuen Konto.
#
# Bleibt erhalten:
#   • alle sichtbaren Ordner und Dateien (Bilder, Dokumente, Musik, Videos,
#     Downloads …)
#   • was auf dem Schreibtisch lag: kommt nach „Dokumente/Vom Schreibtisch DATUM“
#   • Passwort, Alter, Bildschirmzeit, Startbildschirm-Kacheln (liegen im System)
#
# Zurückgesetzt (gelöscht) werden die versteckten Ordner im Konto (.config,
# .local, .mozilla, .var …) – also auch Spielstände. Vorher wird alles davon
# gesichert: /var/lib/serafino/zuruecksetzen/KIND-DATUM.tar.gz
# (nur die letzte Sicherung pro Kind bleibt).
#
# Das Kind darf dabei nicht angemeldet sein.

set -u
K="${1:-}"
die() { echo "$*" >&2; exit 1; }

[[ "$K" =~ ^[a-z_][a-z0-9_-]{0,31}$ ]] || die "Name?"
[ -f "/var/lib/serafino/profiles/$K" ] || die "Kein Kinderkonto."
HOME_K=$(getent passwd "$K" | cut -d: -f6)
[ -n "$HOME_K" ] && [ -d "$HOME_K" ] && [ "$HOME_K" != / ] || die "Kein Benutzerordner."
UG="$(id -u "$K"):$(id -g "$K")"

zustand=$(loginctl show-user "$K" -p State --value 2>/dev/null)
case "$zustand" in
    active|online) die "$K ist noch angemeldet. Bitte erst abmelden (oder den Computer neu starten)." ;;
esac
pkill -KILL -u "$K" 2>/dev/null       # Reste im Hintergrund (z. B. Dienste nach dem Abmelden)

# ---- Schreibtisch-Ordner und Dokumente-Ordner (Namen aus user-dirs.dirs)
xdg() {   # SCHLÜSSEL STANDARD
    local v
    v=$(sed -n "s/^XDG_$1_DIR=\"\$HOME\/\(.*\)\"$/\1/p" "$HOME_K/.config/user-dirs.dirs" 2>/dev/null | head -1)
    echo "${v:-$2}"
}
DESK="$HOME_K/$(xdg DESKTOP Schreibtisch)"
[ -d "$DESK" ] || DESK="$HOME_K/Desktop"
DOKU="$HOME_K/$(xdg DOCUMENTS Dokumente)"
HEUTE=$(date +%Y-%m-%d)

# ---- 1. Sicherung der versteckten Ordner (ohne Zwischenspeicher)
SICH=/var/lib/serafino/zuruecksetzen
mkdir -p "$SICH"; chmod 700 "$SICH"
rm -f "$SICH/$K"-*.tar.gz
( cd "$HOME_K" && find . -maxdepth 1 -name '.?*' ! -name '..' -printf '%P\n' ) > "$SICH/.liste"
if [ -s "$SICH/.liste" ]; then
    tar -C "$HOME_K" --exclude='./.cache' --exclude='.cache' -czf "$SICH/$K-$HEUTE.tar.gz" \
        -T "$SICH/.liste" 2>/dev/null
    echo "Sicherung: $SICH/$K-$HEUTE.tar.gz"
fi
rm -f "$SICH/.liste"

# ---- 2. Schreibtisch leeren: eigene Dateien nach Dokumente, Verknüpfungen weg
if [ -d "$DESK" ]; then
    ZIEL="$DOKU/Vom Schreibtisch $HEUTE"
    find "$DESK" -mindepth 1 -maxdepth 1 | while IFS= read -r f; do
        b=$(basename "$f")
        if [ -L "$f" ] || [[ "$b" == *.desktop ]]; then
            rm -f "$f"                                   # Programm-Symbole kommen neu
        else
            mkdir -p "$ZIEL"; mv -n "$f" "$ZIEL/" 2>/dev/null
        fi
    done
    [ -d "$ZIEL" ] && chown -R "$UG" "$DOKU" && echo "Schreibtisch-Dateien: $ZIEL"
fi

# ---- 3. Versteckte Ordner löschen (Flatpak-Sperre vorher lösen)
FL="$HOME_K/.local/share/flatpak"
[ -d "$FL" ] && chattr -i "$FL" 2>/dev/null
find "$HOME_K" -mindepth 1 -maxdepth 1 -name '.?*' ! -name '..' -exec rm -rf {} +

# ---- 4. Frisch wie ein neues Konto
cp -a --update=none /etc/skel/. "$HOME_K/"
mkdir -p "$DESK"
ln -sfn /usr/share/applications/serafino-youtube-kids.desktop "$DESK/serafino-youtube-kids.desktop"
chown -R "$UG" "$HOME_K"

# ---- 5. Sperren und Regeln wieder anwenden
for s in /usr/local/bin/serafino-kids-flatpak-lock.sh /usr/local/bin/serafino-kids-terminal-lock.sh \
         /usr/local/bin/serafino-kids-noexec.sh /usr/local/bin/serafino-apply-all-ages.py; do
    [ -x "$s" ] && "$s" >/dev/null 2>&1
done
echo "Fertig: $K ist zurückgesetzt."
exit 0
