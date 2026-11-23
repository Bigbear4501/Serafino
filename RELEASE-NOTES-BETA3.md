# Serafino Beta 3

**Serafino** (bisher Pingulinux) ist ein Debian 13 mit KDE Plasma für Kinder von 2 bis 14 Jahren. Mit Beta 3 ist der Name komplett umgestellt: Serafino und das Maskottchen Fino.

Das ist eine **Beta**: zum Ausprobieren und Rückmelden gedacht, noch nicht für den Alltag ohne Aufsicht.

---

## Das Wichtigste in Kürze

- **Vollständige Umbenennung:** Serafino, Fino, Serafino-Befehle, Serafino-Ordner. „Pingulinux“ kommt nicht mehr vor (außer in alten Installationen, die sich beim Update umziehen).
- **Umzug per Update:** Rechner mit Beta 2 bekommen die Umstellung über das Paket-Archiv (`sudo apt update && sudo apt upgrade`), ohne Neuinstallation.
- **Warnung bei BitLocker:** Ist Windows mit BitLocker verschlüsselt, zeigt der Installer vorher einen Hinweis und verweist auf den Wiederherstellungsschlüssel.
- **Hinweis ohne Internet:** Ist der Rechner nicht im WLAN, erscheint vor der Installation ein Hinweis, wie man sich verbindet.
- **Schnelleres Abmelden:** Hängende Programme werden beim Abmelden und Herunterfahren nach 10 Sekunden beendet, nicht erst nach 90.
- **Hilfe-Menü:** Impressum und Datenschutz sind direkt erreichbar. Der Eintrag „Serafino unterstützen“ ist entfernt.

---

## Neu

- **Name und Maskottchen:** Startbild, Anmeldebildschirm und Startmenü zeigen Fino. Die Profilbilder sind Fino.
- **Eltern-Handbuch:** neuer Abschnitt zu BitLocker mit dem Schlüssel unter aka.ms/myrecoverykey und dem Befehl `manage-bde -status`.
- **Lizenzhinweise:** Serafino selbst steht unter GPL-3. Enthalten sind Firmware-Pakete für WLAN und Grafik, die nicht frei im Sinne der Debian-Richtlinien sind. Das steht in README und auf der Webseite.
- **Startbild:** Im Test steht ein einfarbiger weißer Hintergrund (noch nicht im Alltag geprüft).

## Behoben

- Impressum und Datenschutz sind wieder im Hilfe-Menü verlinkt.
- Doppelte Impressum-Datei auf der Webseite bereinigt.
- Veraltete Paketquelle „pingulinux-test“ wird beim Update automatisch entfernt.

---

## Bekannte Einschränkungen

- **BitLocker-Warnung** ist noch nicht auf echter Hardware mit BitLocker-Partition getestet. Sie blockiert die Installation nicht.
- **Netzwerk im Installer:** Calamares hat keine eigene WLAN-Auswahl. Verbindest du dich nicht vorher, zeigt der Installer nur einen Hinweis. Das WLAN-Symbol oben rechts im Panel bleibt der Weg.
- **Startbild:** Der Hintergrund ist noch nicht auf allen Geräten geprüft.
- **Nvidia- und Broadcom-Treiber** sind experimentell und nur auf den Test-Geräten geprüft.

---

## Prüfsumme

Die SHA256-Prüfsumme der ISO steht in der README und in der Datei `SHA256SUMS`. Die Signatur liegt in `SHA256SUMS.asc`.
