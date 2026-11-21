#!/bin/bash
# serafino-umzug-konto.sh – zieht die Einstellungen eines Kontos von Pingulinux
# auf Serafino um: Taskleiste (Restzeit-Widget, angeheftete
# Programme), Fenster-Regeln der Kleinen, Merker, Startmenü-Symbol.
#
# Aufruf: serafino-umzug-konto.sh [HOME-ORDNER]
#   als root aus dem Paket (für alle Konten) und beim Anmelden für das eigene
#   Konto (/etc/xdg/plasma-workspace/env/serafino-umzug.sh). Läuft schnell durch,
#   wenn nichts (mehr) umzuziehen ist.
H="${1:-$HOME}"
[ -d "$H" ] || exit 0

ersetze() {
    # Besitzer bleibt erhalten (GNU sed -i übernimmt ihn)
    sed -i -e 's#/usr/share/pingulinux/icons/pingu\.png#/usr/share/serafino/icons/fino.png#g' \
           -e 's#/usr/share/backgrounds/pingulinux#/usr/share/backgrounds/serafino#g' \
           -e 's#org\.pingulinux\.#org.serafino.#g' \
           -e 's#pingulinux#serafino#g' "$1" 2>/dev/null
}

# 1. Einstellungsdateien
for f in "$H"/.config/plasma-org.kde.plasma.desktop-appletsrc "$H"/.config/plasmashellrc \
         "$H"/.config/kwinrulesrc "$H"/.config/kglobalshortcutsrc "$H"/.config/kickoffrc \
         "$H"/.config/kdeglobals "$H"/.config/mimeapps.list "$H"/.config/kwinrc \
         "$H"/.config/autostart/*.desktop "$H"/.local/share/applications/*.desktop \
         "$H"/Desktop/*.desktop "$H"/Schreibtisch/*.desktop; do
    [ -f "$f" ] && [ ! -L "$f" ] && grep -q pingulinux "$f" 2>/dev/null && ersetze "$f"
done

# 2. Dateien mit altem Namen (z. B. ausgeblendete Programme, Autostart)
for d in "$H"/.local/share/applications "$H"/.config/autostart "$H"/Desktop "$H"/Schreibtisch; do
    for f in "$d"/*pingulinux*; do
        [ -e "$f" ] || continue
        neu="$d/$(basename "$f" | sed 's/pingulinux/serafino/g')"
        [ -e "$neu" ] && rm -f "$f" || mv "$f" "$neu"
    done
done

# 3. Merker-Ordner (Geburtstag gezeigt, Einrichtung später, …)
for d in .local/state .local/share .config .cache; do
    alt="$H/$d/pingulinux"; neu="$H/$d/serafino"
    [ -d "$alt" ] || continue
    if [ -d "$neu" ]; then
        cp -a -n "$alt"/. "$neu"/ 2>/dev/null; rm -rf "$alt"
    else
        mv "$alt" "$neu"
    fi
done
exit 0
