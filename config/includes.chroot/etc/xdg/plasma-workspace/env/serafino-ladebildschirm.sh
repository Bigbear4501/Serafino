# Serafino (v1y): Ladebildschirm mit Fino auch für Konten, in denen KDE
# schon „Breeze“ eingetragen hat oder in denen es (aus der alten Vorlage
# etc/skel,) ganz ausgeschaltet war. Eine eigene Wahl der Eltern bleibt.
# Wird von startplasma eingelesen – kein exit!
_sf_k="$HOME/.config/ksplashrc"
if [ -f "$_sf_k" ] && [ -d /usr/share/plasma/look-and-feel/org.serafino.splash ]; then
    _sf_t=$(sed -n 's/^Theme=//p' "$_sf_k" | head -1)
    case "$_sf_t" in
        ""|None|none|org.kde.breeze.desktop|org.kde.breezedark.desktop|org.kde.breezetwilight.desktop)
            sed -i '/^Theme=/d; /^Engine=/d' "$_sf_k" 2>/dev/null ;;
    esac
fi
unset _sf_k _sf_t
