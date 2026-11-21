#!/bin/bash
# serafino-starter-aufraeumen.sh – keine leeren Symbole in der Taskleiste,
# Fino auf dem Startmenü-Knopf (bz36)
#
# Läuft bei jeder Anmeldung (alle Konten, alle Altersstufen). Entfernt aus der
# Taskleiste angeheftete Programme, die es auf diesem Rechner nicht (mehr) gibt
# oder die für dieses Konto gesperrt sind (z. B. Krita für ein 8-jähriges Kind,
# alter Name gcompris-qt.desktop). Sonst zeigt KDE dort ein leeres Symbol mit
# dem Dateinamen als Hinweis.
set -u
command -v qdbus6 >/dev/null 2>&1 || exit 0
CFG="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"

# warten, bis Plasma läuft (und die Erst-Einrichtung ihre Leiste geschrieben hat)
for i in $(seq 1 60); do
    qdbus6 org.kde.plasmashell /PlasmaShell >/dev/null 2>&1 && break
    sleep 1
done
sleep 10
[ -f "$CFG" ] || exit 0

TOT=$(python3 - "$CFG" <<'PY'
import os, re, sys
home = os.path.expanduser("~")
DIRS = [os.path.join(home, ".local/share/applications"), "/usr/share/applications",
        "/usr/local/share/applications", "/var/lib/flatpak/exports/share/applications",
        os.path.join(home, ".local/share/flatpak/exports/share/applications")]
def tot(name):
    for d in DIRS:
        p = os.path.join(d, name)
        if os.path.exists(p):
            try:
                t = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                return False
            # vom Konto ausgeblendet (gesperrt für dieses Kind) = für dieses Konto tot
            return bool(re.search(r"^(NoDisplay|Hidden)=true", t, re.M))
    return True
namen = set()
for z in open(sys.argv[1], encoding="utf-8", errors="replace"):
    if z.startswith("launchers="):
        namen.update(re.findall(r"(?:applications:|file://[^,]*/)([A-Za-z0-9_.+-]+\.desktop)", z))
print(" ".join(sorted(n for n in namen if tot(n))))
PY
)
LISTE="[]"
[ -n "$TOT" ] && { LISTE=$(printf '"%s",' $TOT); LISTE="[${LISTE%,}]"; }
FINO=/usr/share/serafino/icons/fino.png
qdbus6 org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
var tot = $LISTE;
var ps = panels();
for (var i = 0; i < ps.length; i++) {
  var ws = ps[i].widgets();
  for (var j = 0; j < ws.length; j++) {
    var w = ws[j];
    // Startmenü-Knopf zeigt Fino (bz36)
    if ((w.type == 'org.kde.plasma.kickoff' || w.type == 'org.kde.plasma.kicker' || w.type == 'org.kde.plasma.kickerdash') && '$FINO') {
      w.currentConfigGroup = ['General'];
      if (w.readConfig('icon', '') != '$FINO') { w.writeConfig('icon', '$FINO'); w.reloadConfig(); }
    }
    if (w.type != 'org.kde.plasma.icontasks' && w.type != 'org.kde.plasma.taskmanager') continue;
    w.currentConfigGroup = ['General'];
    var l = w.readConfig('launchers', []);
    if (typeof l == 'string') l = l.length ? l.split(',') : [];
    var neu = [];
    for (var k = 0; k < l.length; k++) {
      var weg = false;
      for (var t = 0; t < tot.length; t++) if (l[k].indexOf(tot[t]) >= 0 && l[k].slice(-tot[t].length) == tot[t]) weg = true;
      if (!weg) neu.push(l[k]);
    }
    if (neu.length != l.length) { w.writeConfig('launchers', neu); w.reloadConfig(); }
  }
}" >/dev/null 2>&1
exit 0
