#!/usr/bin/env python3
"""Ergänzt „contrib non-free“ bei den Debian-Quellen (nötig für Nvidia- und
Broadcom-Treiber). Versteht sources.list (eine Zeile pro Quelle) und das
neue Format (*.sources, „Components:“). Ändert nur Debian-Quellen.
Gibt aus, welche Dateien geändert wurden."""
import glob, re, shutil

NEU = ["main", "contrib", "non-free", "non-free-firmware"]
geaendert = []

def ergaenzen(teile):
    vorher = list(teile)
    for c in NEU:
        if c not in teile:
            teile.append(c)
    return teile, teile != vorher

for f in ["/etc/apt/sources.list"] + glob.glob("/etc/apt/sources.list.d/*.list"):
    try:
        zeilen = open(f, encoding="utf-8").read().splitlines()
    except OSError:
        continue
    neu, anders = [], False
    for z in zeilen:
        m = re.match(r"^(\s*deb(?:-src)?\s+(?:\[[^\]]*\]\s+)?\S*debian\S*\s+\S+)\s+(.+)$", z)
        if m and not z.lstrip().startswith("#"):
            komp, a = ergaenzen(m.group(2).split())
            if a:
                z = m.group(1) + " " + " ".join(komp)
                anders = True
        neu.append(z)
    if anders:
        shutil.copy2(f, f + ".vor-treiber")
        open(f, "w", encoding="utf-8").write("\n".join(neu) + "\n")
        geaendert.append(f)

for f in glob.glob("/etc/apt/sources.list.d/*.sources"):
    try:
        text = open(f, encoding="utf-8").read()
    except OSError:
        continue
    bloecke, anders = text.split("\n\n"), False
    for i, b in enumerate(bloecke):
        if not re.search(r"^URIs:.*debian", b, re.M):
            continue
        m = re.search(r"^Components:\s*(.*)$", b, re.M)
        if m:
            komp, a = ergaenzen(m.group(1).split())
            if a:
                bloecke[i] = b[:m.start()] + "Components: " + " ".join(komp) + b[m.end():]
                anders = True
    if anders:
        shutil.copy2(f, f + ".vor-treiber")
        open(f, "w", encoding="utf-8").write("\n\n".join(bloecke))
        geaendert.append(f)

print(" ".join(geaendert))
