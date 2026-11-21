#!/bin/bash
# serafino-restzeit-leiste.sh – läuft beim Anmelden (Autostart).
# Kinderkonto: setzt die Anzeige „⏳ Noch 45 Min“ (Plasma-Widget
# org.serafino.restzeit) in die Taskleiste, falls sie dort noch fehlt.
# Eltern-Konten: nichts. Das Widget ist ohne Zeitbegrenzung unsichtbar.
U=$(id -un)
[ -f "/var/lib/serafino/profiles/$U" ] || exit 0
QDBUS=$(command -v qdbus6 || command -v qdbus) || exit 0
# warten, bis die Plasma-Oberfläche bereit ist (höchstens 60 s)
for _ in $(seq 1 30); do
    "$QDBUS" org.kde.plasmashell /PlasmaShell >/dev/null 2>&1 && break
    sleep 2
done
read -r -d '' JS <<'JSEND'
var ps = panels();
for (var i = 0; i < ps.length; i++) {
    var p = ps[i], da = false, w = p.widgets();
    for (var j = 0; j < w.length; j++) {
        if (w[j].type == "org.serafino.restzeit") { da = true; }
    }
    if (!da) { p.addWidget("org.serafino.restzeit"); }
}
JSEND
"$QDBUS" org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$JS" >/dev/null 2>&1
exit 0
