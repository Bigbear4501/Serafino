# Getestete Geräte

Auf diesen Geräten läuft Serafino nachweislich. Die Liste wächst – **melde gern dein Gerät** (siehe unten).

Serafino basiert auf Debian 13. Was dort läuft, läuft meist auch hier: Die meisten Laptops und PCs mit 64-Bit-Prozessor ab etwa 2010, mindestens 4 GB Arbeitsspeicher und 32 GB Festplatte.

**Getestet** heißt: Jemand hat Serafino darauf gestartet und die wichtigsten Dinge ausprobiert – WLAN, Ton, Bildschirm, Tastatur und Maus bzw. Touch, Kinderkonten und Bildschirmzeit.

| Gerät | Baujahr / Ausstattung | Getestet | Ergebnis |
|---|---|---|---|
| **Microsoft Surface Go 2** | Intel, Touchscreen | installiert, Secure Boot an | ✅ Alles geht: Touch, Bildschirmtastatur, WLAN, Ton, Kernel-Wechsel (Backports). Optisch: beim Startbild manchmal bunte Streifen am oberen Rand |
| **Apple MacBook Air** | 2011, Intel Core i5, 4 GB RAM, 128 GB SSD | installiert | ✅ Alles geht, auch WLAN. Vom Stick starten: beim Einschalten die **Alt-Taste** gedrückt halten |
| **Stand-PC (Eigenbau)** | AMD Ryzen 5 3600X, 32 GB RAM, 1,5 TB SSD, AMD Radeon RX 5000/6000 (8 GB) | ausprobiert | ✅ Alles geht. AMD-Grafik braucht keinen zusätzlichen Treiber |
| **Laptop mit Nvidia GeForce** (2 Geräte) | Intel, Nvidia-Grafik | Live-Modus | ✅ Startet, Grafik wird erkannt, „Hardware & Treiber“ bietet den Nvidia-Treiber an. ⚠️ Installation des Nvidia-Treibers noch nicht getestet |
| **Virtuelle Maschine** (GNOME Boxes / QEMU) | 4 GB RAM, UEFI und BIOS | installiert | ✅ Alles geht (ohne WLAN – dort gibt es nur Kabel-Netz) |

## Gut zu wissen

- **Nvidia-Grafik:** Serafino startet mit dem freien Treiber. Den Treiber von Nvidia bietet das Kontrollzentrum unter „Hardware & Treiber“ an. Bei eingeschaltetem Secure Boot erscheint nach dem Neustart einmal ein blauer Bildschirm, auf dem du den neuen Treiber-Schlüssel bestätigst – das Kontrollzentrum erklärt vorher, was zu tun ist. (Noch nicht auf echter Hardware getestet.)
- **Broadcom-WLAN** (häufig in älteren Laptops und Macs): Manche Chips brauchen einen zusätzlichen Treiber, den „Hardware & Treiber“ ebenfalls anbietet.
- **Secure Boot** darf eingeschaltet bleiben.
- **Windows mit BitLocker:** Der Installer warnt dich – siehe [Installationsanleitung](INSTALLATION.md).

## Dein Gerät melden

Du hast Serafino auf einem anderen Gerät ausprobiert? Schreib es uns im [Forum unter „Zeigt her“](../../discussions) – egal, ob alles lief oder etwas nicht ging. Am besten mit dieser Ausgabe (Konsole öffnen, einfügen, Enter):

```
cat /sys/class/dmi/id/sys_vendor /sys/class/dmi/id/product_name; lspci | grep -iE 'vga|3d|network|audio'
```

Und dazu kurz: Live-Modus oder installiert? WLAN, Ton, Touchpad bzw. Touch, Kamera – was ging, was nicht?
