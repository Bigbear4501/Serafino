#!/bin/bash
# treiber-root.sh  (bz14 „Hardware & Treiber“) – läuft als root, nur über
#   pkexec /usr/local/bin/pingulinux-root-helper treiber nvidia=an|aus|- broadcom=an|aus|- kernel=bpo|debian|-
#   … treiber mok=neu   (nur neuen Secure-Boot-Code erstellen, z. B. blauen Bildschirm verpasst)
# Ausgabe-Zeilen für das Fenster:
#   SCHRITT: <Text>      gerade passiert
#   HINWEIS: <Text>      wichtig für Eltern
#   MOK-CODE: <Ziffern>  Secure Boot: beim nächsten Start eingeben
#   NEUSTART             Neustart nötig
# Exit: 0 gut, 3 Grafikkarte zu alt, 4 Fehler, 5 Live-Modus
set -u
export DEBIAN_FRONTEND=noninteractive
LOG=/var/log/pingulinux-treiber.log
exec > >(tee -a "$LOG") 2>&1
echo "=== $(date '+%F %T') treiber $* ==="

schritt() { echo "SCHRITT: $*"; }
hinweis() { echo "HINWEIS: $*"; }
fehler()  { echo "HINWEIS: $*"; exit 4; }
APT="apt-get -y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold"

NV=-; BC=-; KE=-; MOK=-
for a in "$@"; do
    case "$a" in
        nvidia=an|nvidia=aus|nvidia=-)       NV=${a#*=} ;;
        broadcom=an|broadcom=aus|broadcom=-) BC=${a#*=} ;;
        kernel=bpo|kernel=debian|kernel=-)   KE=${a#*=} ;;
        mok=neu)                             MOK=neu ;;
        *) fehler "Unbekannte Angabe: $a" ;;
    esac
done
[ "$NV$BC$KE" = "---" ] && [ "$MOK" = - ] && { hinweis "Nichts zu tun."; exit 0; }
grep -qw "boot=live" /proc/cmdline && { hinweis "Im Live-Modus geht das nicht – erst Pingulinux installieren."; exit 5; }

installiert() { dpkg-query -W -f='${Status}' "$1" 2>/dev/null | grep -q "install ok installed"; }
NEUSTART=0

if [ "$NV$BC$KE" != "---" ]; then   # ---- Treiber/Kernel ändern ----

# 1. Sicherung (falls Timeshift eingerichtet ist)
if command -v timeshift >/dev/null && [ -s /etc/timeshift/timeshift.json ]; then
    schritt "Sicherung des Systems anlegen (kann ein paar Minuten dauern) …"
    timeshift --create --comments "Vor Hardware & Treiber" --scripted >/dev/null 2>&1 \
        || hinweis "Sicherung hat nicht geklappt – es geht trotzdem weiter."
fi

# 2. Paketquellen: contrib und non-free dazu (Nvidia, Broadcom)
if [ "$NV" = an ] || [ "$BC" = an ]; then
    schritt "Paketquellen für Treiber freischalten …"
    python3 /usr/local/lib/pingulinux/quellen-nonfree.py >/dev/null || fehler "Paketquellen konnten nicht geändert werden."
fi
# Backports-Quelle eintragen, falls sie fehlt (sonst gibt es keinen neueren Kernel)
if [ "$KE" = bpo ] && ! grep -rqs --include='*.list' --include='*.sources' -e 'trixie-backports' /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null \
   && ! grep -qs 'trixie-backports' /etc/apt/sources.list; then
    schritt "Backports-Quelle eintragen …"
    printf 'deb http://deb.debian.org/debian trixie-backports main contrib non-free-firmware\n' \
        > /etc/apt/sources.list.d/pingulinux-backports.list
fi
schritt "Paketlisten aktualisieren …"
apt-get update -qq || fehler "Keine Verbindung zu den Paketquellen. Ist der Computer mit dem Internet verbunden?"

# Backports-Kernel erkennt man an der VERSION („~bpo13“), nicht am Namen:
# linux-image-7.2.12+deb13-amd64 hat Version 7.2.12-1~bpo13+1.
bpo_pakete() {   # installierte Kernel-, Header- und kbuild-Pakete aus Backports (ohne Metapakete)
    dpkg-query -W -f='${Package} ${Version} ${Status}\n' 'linux-image-[0-9]*' 'linux-headers-[0-9]*' 'linux-kbuild-[0-9]*' 2>/dev/null \
        | awk '$2 ~ /bpo/ && /install ok installed/ {print $1}'
}
laeuft_bpo() { dpkg-query -W -f='${Version}' "linux-image-$(uname -r)" 2>/dev/null | grep -q bpo; }

# 3. Kernel
if [ "$KE" = bpo ]; then
    schritt "Neuen Kernel und Firmware aus Backports installieren …"
    FW=$(dpkg-query -W -f='${Package} ${Status}\n' 'firmware-*' 2>/dev/null | awk '/install ok installed/{print $1}')
    HD=""; installiert dkms && HD="linux-headers-amd64"
    # shellcheck disable=SC2086
    $APT install -t trixie-backports linux-image-amd64 $HD $FW || fehler "Der neue Kernel konnte nicht installiert werden."
    rm -f /var/lib/pingulinux/kernel-aufraeumen
    NEUSTART=1
elif [ "$KE" = debian ]; then
    schritt "Zurück zum Kernel von Debian 13 …"
    HD=""; installiert linux-headers-amd64 && HD="linux-headers-amd64/trixie"
    # shellcheck disable=SC2086
    $APT install --allow-downgrades linux-image-amd64/trixie $HD || fehler "Der Debian-13-Kernel konnte nicht installiert werden."
    STABIL=$(dpkg-query -W -f='${Package} ${Version} ${Status}\n' 'linux-image-[0-9]*' 2>/dev/null \
        | awk '$2 !~ /bpo/ && /install ok installed/ {sub(/^linux-image-/,"",$1); print $1}' | sort -V | tail -1)
    [ -n "$STABIL" ] || fehler "Kein Debian-13-Kernel gefunden."
    # Backports-Kernel gleich entfernen – auch wenn er gerade läuft. Ohne Rückfragen
    # (DEBIAN_FRONTEND=noninteractive) erlaubt Debian das (linux-check-removal).
    # Bis zum Neustart läuft alles weiter; danach startet nur noch Debian 13.
    schritt "Backports-Kernel entfernen …"
    P=$(bpo_pakete)
    if [ -n "$P" ]; then
        # shellcheck disable=SC2086
        $APT purge $P; RC=$?
        if [ $RC -ne 0 ]; then
            # Rückfall: einmal mit dem Debian-13-Kernel starten, danach räumt ein Dienst auf
            echo "$STABIL" > /var/lib/pingulinux/kernel-aufraeumen
            systemctl enable pingulinux-kernel-aufraeumen.service >/dev/null 2>&1
            hinweis "Der Backports-Kernel wird nach dem Neustart entfernt."
        fi
    fi
    # Reste eines älteren Wechsels (Startmenü merkte sich einen Eintrag) aufräumen
    rm -f /etc/default/grub.d/50-pingulinux-kernel.cfg
    update-grub >/dev/null 2>&1
    grub-set-default 0 >/dev/null 2>&1
    NEUSTART=1
fi

# Header für den Kernel, mit dem nach dem Neustart gestartet wird (sonst baut DKMS den Treiber für den falschen)
if [ "$KE" = bpo ] || { [ "$KE" = - ] && laeuft_bpo; }; then
    HD="-t trixie-backports linux-headers-amd64"
else
    HD="linux-headers-amd64"
fi
KOPF="linux-headers-$(uname -r)"
[ "$KE" != - ] && KOPF=""                 # neuer/alter Kernel bringt seine Header über das Metapaket

# 4. Nvidia
NVPAKETE() { dpkg-query -W -f='${Package} ${Status}\n' 2>/dev/null | awk '/install ok installed/{print $1}' \
    | grep -E '^(nvidia-|libnvidia-|xserver-xorg-video-nvidia|firmware-nvidia|libcuda|libnvcuvid|libnvoptix|lib(gl|egl|gles|glx)1?-nvidia|libegl-nvidia|libgles-nvidia|libglx-nvidia)' \
    | grep -v '^nvidia-detect$'; }
if [ "$NV" = an ]; then
    schritt "Passenden Nvidia-Treiber suchen …"
    $APT install nvidia-detect >/dev/null || fehler "nvidia-detect konnte nicht installiert werden."
    EMPF=$(nvidia-detect 2>/dev/null | grep -A1 -i "recommended to install" | tail -1 | tr -d ' ')
    case "$EMPF" in
        nvidia-driver|nvidia-tesla-535-driver)
            schritt "Nvidia-Treiber installieren ($EMPF) – das dauert ein paar Minuten …"
            # shellcheck disable=SC2086
            # switcheroo-control: bei Laptops mit zwei Grafikchips bietet KDE dann
            # „Mit dedizierter Grafikkarte starten“ an (Nvidia nur für Spiele)
            $APT install $HD $KOPF "$EMPF" firmware-misc-nonfree switcheroo-control || fehler "Der Nvidia-Treiber konnte nicht installiert werden."
            mkdir -p /etc/modprobe.d
            printf 'options nvidia-drm modeset=1 fbdev=1\n' > /etc/modprobe.d/pingulinux-nvidia.conf
            NEUSTART=1 ;;
        *)
            hinweis "Diese Nvidia-Grafikkarte ist zu alt für die Treiber von Debian 13. Sie läuft weiter mit dem freien Treiber (nouveau)."
            exit 3 ;;
    esac
elif [ "$NV" = aus ]; then
    schritt "Nvidia-Treiber entfernen …"
    P=$(NVPAKETE)
    # shellcheck disable=SC2086
    [ -n "$P" ] && { $APT purge $P || fehler "Der Nvidia-Treiber konnte nicht entfernt werden."; }
    rm -f /etc/modprobe.d/pingulinux-nvidia.conf
    NEUSTART=1
fi

# 5. Broadcom-WLAN (wl)
if [ "$BC" = an ]; then
    schritt "Broadcom-WLAN-Treiber installieren …"
    # shellcheck disable=SC2086
    $APT install $HD $KOPF broadcom-sta-dkms || fehler "Der Broadcom-Treiber konnte nicht installiert werden."
    if [ "$KE" = - ]; then                 # sofort laden, wenn möglich (sonst nach dem Neustart)
        modprobe -r b44 b43 b43legacy ssb brcmsmac bcma 2>/dev/null
        modprobe wl 2>/dev/null || NEUSTART=1
    else
        NEUSTART=1
    fi
elif [ "$BC" = aus ]; then
    schritt "Broadcom-WLAN-Treiber entfernen …"
    $APT purge broadcom-sta-dkms || fehler "Der Broadcom-Treiber konnte nicht entfernt werden."
    NEUSTART=1
fi

fi   # ---- Ende Treiber/Kernel ----

# 6. Secure Boot: eigene Treiber (DKMS) müssen signiert sein. Der Schlüssel
#    muss einmal beim Start bestätigt werden (blauer Bildschirm „MOK“).
if installiert dkms && mokutil --sb-state 2>/dev/null | grep -qi "SecureBoot enabled"; then
    KEY=/var/lib/dkms/mok.pub
    [ -f "$KEY" ] || dkms generate_mok >/dev/null 2>&1
    if [ -f "$KEY" ] && ! mokutil --test-key "$KEY" 2>/dev/null | grep -qi "already enrolled"; then
        [ "$MOK" = neu ] && mokutil --revoke-import >/dev/null 2>&1   # alten, nicht bestätigten Code verwerfen
        schritt "Secure Boot: Schlüssel für die Treiber vorbereiten …"
        CODE=$(tr -dc '0-9' < /dev/urandom | head -c 8)
        if printf '%s\n%s\n' "$CODE" "$CODE" | mokutil --import "$KEY" >/dev/null 2>&1; then
            echo "MOK-CODE: $CODE"
            NEUSTART=1
        else
            hinweis "Secure Boot: Der Schlüssel konnte nicht vorgemerkt werden. Der Treiber startet erst, wenn Secure Boot im BIOS aus ist."
        fi
    fi
fi

[ "$NEUSTART" = 1 ] && echo "NEUSTART"
echo "SCHRITT: Fertig."
exit 0
