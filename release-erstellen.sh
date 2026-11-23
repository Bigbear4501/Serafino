#!/bin/bash
#
# release-erstellen.sh – Serafino-Release vorbereiten (v1g)
#
# Macht aus der frisch gebauten ISO ein fertiges Release:
#   1. ISO umbenennen (serafino-beta3-amd64.iso) und in release/beta3/ legen
#   2. Prüfsumme SHA256SUMS erzeugen
#   3. Prüfsumme mit dem Serafino-Schlüssel unterschreiben (SHA256SUMS.asc)
#      und den öffentlichen Schlüssel dazulegen (serafino-archiv.asc)
#   4. CHANGELOG.md um einen Abschnitt mit allen Änderungen seit dem letzten
#      Release ergänzen (aus den Git-Commits – danach von Hand glätten)
#   5. Die nächsten Schritte anzeigen (Hochladen, README, Tag)
#
# Aufruf im Projektordner (~/kids-distro):
#   bash release-erstellen.sh "Beta 3"
#   bash release-erstellen.sh "Beta 3" pfad/zur.iso
#
# Der private Schlüssel bleibt auf diesem Rechner – unterschrieben wird hier.

set -u
NAME="${1:-}"
[ -n "$NAME" ] || { echo "Aufruf: bash release-erstellen.sh \"Beta 3\" [ISO]"; exit 2; }
ISO="${2:-live-image-amd64.hybrid.iso}"
KURZ=$(echo "$NAME" | tr 'A-Z' 'a-z' | tr -d ' ')          # "Beta 3" → beta3
ORDNER=$(echo "$NAME" | tr ' ' '-')                         # "Beta 3" → Beta-3
ZIEL="release/$KURZ"
DATEI="serafino-$KURZ-amd64.iso"

ok()   { echo "  ✓ $1"; }
warn() { echo "  ⚠ $1"; }
stopp(){ echo "  ✗ $1"; exit 1; }

echo "== Serafino-Release: $NAME =="

[ -d config ] || stopp "Bitte im Projektordner starten (cd ~/kids-distro)."
[ -f "$ISO" ] || stopp "ISO nicht gefunden: $ISO (erst bauen, oder Pfad angeben)"

# 0. Vorab-Prüfung (warnt nur)
if [ -x ./release-check.sh ] || [ -f ./release-check.sh ]; then
    bash ./release-check.sh >/dev/null 2>&1 && ok "release-check.sh ohne Fehler" \
        || warn "release-check.sh meldet etwas – bitte danach: bash release-check.sh"
fi

# 1. ISO in den Release-Ordner (ohne 2,7 GB zu kopieren, wenn möglich)
mkdir -p "$ZIEL"
rm -f "$ZIEL/$DATEI"
ln "$ISO" "$ZIEL/$DATEI" 2>/dev/null || cp "$ISO" "$ZIEL/$DATEI" || stopp "ISO konnte nicht nach $ZIEL kopiert werden"
ok "ISO: $ZIEL/$DATEI ($(du -h "$ZIEL/$DATEI" | cut -f1))"

# 2. Prüfsumme
(cd "$ZIEL" && sha256sum "$DATEI" > SHA256SUMS) || stopp "Prüfsumme fehlgeschlagen"
SUMME=$(cut -d' ' -f1 "$ZIEL/SHA256SUMS")
ok "SHA256: $SUMME"

# 3. Unterschrift
SCHLUESSEL=""
for k in "Serafino Paketarchiv" "Pingulinux Paketarchiv"; do
    gpg --batch --list-secret-keys "$k" >/dev/null 2>&1 && { SCHLUESSEL="$k"; break; }
done
if [ -n "$SCHLUESSEL" ]; then
    rm -f "$ZIEL/SHA256SUMS.asc"
    gpg --armor --detach-sign -u "$SCHLUESSEL" -o "$ZIEL/SHA256SUMS.asc" "$ZIEL/SHA256SUMS" \
        && ok "SHA256SUMS unterschrieben (SHA256SUMS.asc)" || warn "Unterschreiben hat nicht geklappt"
    gpg --armor --export "$SCHLUESSEL" > "$ZIEL/serafino-archiv.asc"
    gpg --verify "$ZIEL/SHA256SUMS.asc" "$ZIEL/SHA256SUMS" >/dev/null 2>&1 && ok "Unterschrift geprüft"
else
    warn "Kein Serafino-Schlüssel gefunden – Release ist NICHT unterschrieben"
fi

# 4. Changelog
DATUM=$(date +%d.%m.%Y)
if grep -q "^## Serafino $NAME " CHANGELOG.md 2>/dev/null; then
    ok "CHANGELOG.md hat schon einen Abschnitt „$NAME“ – nicht geändert"
else
    VORHER=$(git describe --tags --abbrev=0 2>/dev/null || true)
    BEREICH="${VORHER:+$VORHER..}HEAD"
    AENDERUNGEN=$(git log "$BEREICH" --no-merges --format='%s' 2>/dev/null \
        | grep -vE '^(Add files via upload|Delete |Update |Create |Rename |Merge )' \
        | sed 's/^/- /' | awk '!seen[$0]++')
    [ -n "$AENDERUNGEN" ] || AENDERUNGEN="- (keine Commits gefunden)"
    {
        echo "# Serafino – Änderungen"
        echo
        echo "## Serafino $NAME ($DATUM)"
        echo
        if [ -n "$VORHER" ]; then echo "Seit ${VORHER}:"; echo; fi
        echo "$AENDERUNGEN"
        echo
        if [ -f CHANGELOG.md ]; then sed '1{/^# Serafino – Änderungen$/d}' CHANGELOG.md | sed '1{/^$/d}'; fi
    } > CHANGELOG.md.neu
    mv CHANGELOG.md.neu CHANGELOG.md
    ok "CHANGELOG.md: Abschnitt „$NAME“ ergänzt ($(echo "$AENDERUNGEN" | wc -l) Einträge seit ${VORHER:-Anfang}) – bitte durchlesen und glätten"
fi
grep -q '^release/' .gitignore 2>/dev/null || { echo 'release/' >> .gitignore; ok "release/ in .gitignore (die ISO kommt nicht zu GitHub)"; }

# 5. Nächste Schritte
cat <<EOF

== Fertig vorbereitet. Nächste Schritte ==

1) CHANGELOG.md durchlesen (Commit-Texte glätten, Überraschungen nicht erwähnen)
   und die Release Notes RELEASE-NOTES-${KURZ^^}.md schreiben.

2) Hochladen zu SourceForge (Ordner $ORDNER, dein SourceForge-Benutzername statt BENUTZER):
   rsync -avP $ZIEL/ BENUTZER@frs.sourceforge.net:/home/frs/project/serafino/$ORDNER/

3) README: Download-Link und Prüfsumme eintragen
   https://sourceforge.net/projects/serafino/files/$ORDNER/$DATEI/download
   SHA256: $SUMME

4) Hochladen zu GitHub und markieren:
   git add -A && git commit -m "Serafino $NAME" && git push
   git tag $KURZ && git push --tags
EOF
