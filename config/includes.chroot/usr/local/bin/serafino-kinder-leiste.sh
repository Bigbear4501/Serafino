#!/bin/bash
#
# serafino-kinder-leiste.sh weg|zurueck   (läuft im Kinderkonto, be4n)
#
#   weg      Startbildschirm der Kleinen: Plasma-Leiste ganz entfernen. Bei den
#            Kleinen gibt es nur das Programm und den 🏠-Knopf – keine Taskleiste,
#            über die man Fenster wechseln, minimieren oder ins Menü kommt.
#   zurueck  Konto hat keinen Startbildschirm (mehr), z. B. ab 7 Jahren oder von
#            den Eltern ausgeschaltet: Standard-Leiste wieder anlegen, falls
#            keine da ist, mit der Restzeit-Anzeige.
#
# Plasma muss dafür laufen – das Skript wartet bis zu 60 Sekunden darauf.

[ -f "/var/lib/serafino/profiles/$(id -un)" ] || exit 0        # nur Kinderkonten
QDBUS=$(command -v qdbus6 || command -v qdbus) || exit 0
for _ in $(seq 1 30); do
    "$QDBUS" org.kde.plasmashell /PlasmaShell >/dev/null 2>&1 && break
    sleep 2
done

case "${1:-}" in
    weg)
        JS='var ps = panels(); for (var i = 0; i < ps.length; i++) { ps[i].remove(); }'
        ;;
    zurueck)
        read -r -d '' JS <<'JSEND'
if (panels().length == 0) {
    loadTemplate("org.kde.plasma.desktop.defaultPanel");
}
var ps = panels();
for (var i = 0; i < ps.length; i++) {
    var da = false, w = ps[i].widgets();
    for (var j = 0; j < w.length; j++) {
        if (w[j].type == "org.serafino.restzeit") { da = true; }
    }
    if (!da) { ps[i].addWidget("org.serafino.restzeit"); }
}
JSEND
        ;;
    *) echo "Aufruf: $0 weg|zurueck" >&2; exit 2 ;;
esac
"$QDBUS" org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "$JS" >/dev/null 2>&1
exit 0
