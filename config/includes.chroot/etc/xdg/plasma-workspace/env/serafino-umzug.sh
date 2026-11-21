# Serafino: Einstellungen dieses Kontos von Pingulinux umziehen,
# bevor Plasma startet (sonst schreibt Plasma die alten Namen zurück).
if [ -x /usr/local/lib/serafino/serafino-umzug-konto.sh ] && \
   grep -qs pingulinux "$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc" "$HOME/.config/kwinrulesrc"; then
    /usr/local/lib/serafino/serafino-umzug-konto.sh "$HOME" >/dev/null 2>&1
fi
