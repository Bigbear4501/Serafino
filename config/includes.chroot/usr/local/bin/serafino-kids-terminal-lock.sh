#!/bin/bash
#
# serafino-kids-terminal-lock.sh  (läuft als root, beim Start und wenn
# sich Kinderkonten ändern)
#
# Kinder bekommen kein Terminal. Gesperrt werden die Terminal-Programme
# (Konsole, früher xfce4-terminal) und das eingebaute Terminal von Dolphin
# (F4, „konsolepart“). Eltern sind nicht betroffen.
# Technik: Zugriffsliste (ACL) „kein Zugriff“ für das jeweilige Kinderkonto.

DATA="${FINO_DATA:-/var/lib/serafino}"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
run() { if [ $DRY = 1 ]; then echo "[dry-run] $*"; else "$@"; fi; }
is_kid() { [ -e "$DATA/birth/$1" ] || [ -e "$DATA/profiles/$1" ]; }

command -v setfacl >/dev/null || { echo "setfacl fehlt (Paket acl)" >&2; exit 0; }

targets=()
for f in /usr/bin/konsole /usr/bin/xfce4-terminal /usr/bin/xterm /usr/bin/uxterm; do
    [ -e "$f" ] && targets+=("$(readlink -f "$f")")
done
while IFS= read -r f; do targets+=("$f"); done < <(find /usr/lib -name 'konsolepart.so' 2>/dev/null)
[ ${#targets[@]} -eq 0 ] && exit 0

# Strg+Alt+T: Kinder sehen Fino („Das ist nur für Erwachsene.“) statt nichts.
# Eigener Menüeintrag im Kinderkonto, der den Konsole-Eintrag überdeckt.
MARK="X-Serafino-Hidden=true"
fino_terminal() {   # BENUTZER HOME an|aus
    local d="$2/.local/share/applications" f="$2/.local/share/applications/org.kde.konsole.desktop"
    if [ "$3" = an ]; then
        [ -e "$f" ] && ! grep -q "$MARK" "$f" && return       # eigene Datei des Kindes nicht anfassen
        [ $DRY = 1 ] && { echo "[dry-run] Fino-Terminal für $1"; return; }
        mkdir -p "$d"
        printf '[Desktop Entry]\nType=Application\nName=Konsole\nNoDisplay=true\nExec=/usr/local/bin/serafino-kind-hinweis.py --terminal\nX-KDE-Shortcuts=Ctrl+Alt+T\n%s\n' "$MARK" > "$f"
        chown "$1:" "$2/.local" "$2/.local/share" "$d" "$f" 2>/dev/null
    elif [ -e "$f" ] && grep -q "$MARK" "$f"; then
        run rm -f "$f"
    fi
}

getent passwd | while IFS=: read -r user _ uid _ _ home _; do
    [ "$uid" -ge 1000 ] 2>/dev/null && [ "$uid" -lt 60000 ] || continue
    case "$home" in /home/*) ;; *) continue ;; esac
    for t in "${targets[@]}"; do
        if is_kid "$user"; then
            getfacl -cp "$t" 2>/dev/null | grep -qx "user:$user:---" || run setfacl -m "u:$user:---" "$t"
        else
            getfacl -cp "$t" 2>/dev/null | grep -q "^user:$user:" && run setfacl -x "u:$user" "$t"
        fi
    done
    if is_kid "$user"; then fino_terminal "$user" "$home" an; else fino_terminal "$user" "$home" aus; fi
done
exit 0
