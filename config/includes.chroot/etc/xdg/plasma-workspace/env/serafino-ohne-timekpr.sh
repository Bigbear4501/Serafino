# Serafino (bz31): Timekpr-Symbol und Timekpr-Meldungen („genug Zeit“ usw.)
# in allen Konten ausblenden. Timekpr arbeitet im Hintergrund weiter (Zeitkonto,
# Abmelden); Kinder sehen die eigene Restzeit-Anzeige und Finos Hinweise.
# Läuft vor dem Plasma-Autostart (wird von startplasma eingelesen – kein exit!).
for _sf_a in /etc/xdg/autostart/timekpr*.desktop; do
    [ -f "$_sf_a" ] || continue
    _sf_z="$HOME/.config/autostart/$(basename "$_sf_a")"
    if ! grep -qs '^Hidden=true' "$_sf_z"; then
        mkdir -p "$HOME/.config/autostart" 2>/dev/null
        printf '[Desktop Entry]\nType=Application\nName=Timekpr (von Serafino ausgeblendet)\nHidden=true\n' > "$_sf_z" 2>/dev/null
    fi
done
unset _sf_a _sf_z
