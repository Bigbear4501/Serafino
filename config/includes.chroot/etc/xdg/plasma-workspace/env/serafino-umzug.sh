# Serafino: Einstellungen dieses Kontos von Pingulinux umziehen,
# bevor Plasma startet (sonst schreibt Plasma die alten Namen zurück).
if [ -x /usr/local/lib/serafino/serafino-umzug-konto.sh ]; then
    if grep -qs pingulinux "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc" "$HOME/.config/kwinrulesrc" \
       || ls "$HOME"/Desktop/*pingulinux* "$HOME"/Schreibtisch/*pingulinux* "$HOME"/.local/share/applications/*pingulinux* >/dev/null 2>&1 \
       || { [ -f "$HOME/.face" ] && ! [ -e "$HOME/.local/state/serafino/.face-geprueft" ]; }; then
        mkdir -p "$HOME/.local/state/serafino" && touch "$HOME/.local/state/serafino/.face-geprueft"
        /usr/local/lib/serafino/serafino-umzug-konto.sh "$HOME" >/dev/null 2>&1
    fi
fi
