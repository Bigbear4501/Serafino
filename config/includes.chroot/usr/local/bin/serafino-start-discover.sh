#!/bin/bash
#
# serafino-start-discover.sh
#
# Startet Discover (plasma-discover) und benennt das Fenster im
# Hintergrund in "Serafino App Store" um, da der Fenstertitel
# fest im Programm steckt und nicht über einfache Konfiguration
# änderbar ist.

plasma-discover &
DISCOVER_PID=$!

(
    for i in $(seq 1 30); do
        if command -v wmctrl &> /dev/null; then
            if wmctrl -l | grep -qi "discover"; then
                wmctrl -r "Discover" -N "Serafino App Store"
                break
            fi
        fi
        sleep 0.5
    done
) &

wait "$DISCOVER_PID"
