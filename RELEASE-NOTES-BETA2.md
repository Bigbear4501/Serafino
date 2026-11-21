# Serafino Beta 2

**Serafino** (bisher Pingulinux) ist ein Debian 13 mit KDE Plasma für Kinder von 2 bis 14 Jahren – mit Kinderschutz, Bildschirmzeit und einem Eltern-Kontrollzentrum. Begleitet wird alles von **Fino**, unserem Maskottchen.

> **Hinweis zum Namen:** Neue Teile heißen schon Serafino. An einigen Stellen steht noch „Pingulinux“ (z. B. Paketname `pingulinux-system`, Ordner, Fenstertitel). Die vollständige Umbenennung kommt mit Beta 3.

Das ist eine **Beta**: zum Ausprobieren und Rückmelden gedacht, noch nicht für den Alltag ohne Aufsicht.

---

## Das Wichtigste in Kürze

- **Eigener Startbildschirm für die Kleinen (2–6 Jahre):** große Kacheln, Namen werden vorgelesen, nur das Programm und ein Haus-Knopf – kein Weg in den Eltern-Bereich.
- **Bildschirmzeit, die mitdenkt:** Lernprogramme zählen nicht, Spiele und Videos schon. „Mehr Zeit bitte“ mit Eltern-Passwort, Pausen-Erinnerung von Fino.
- **Updates von selbst:** Serafino hat jetzt ein eigenes, signiertes Paketarchiv. Neue Funktionen und Fehlerbehebungen kommen automatisch – ohne neue ISO.
- **App Store mit 108 Programmen** (83 aus Debian, 25 als Flatpak), jedes mit Mindestalter.
- **WLAN für alle:** Verbinden sich die Eltern mit einem WLAN, sind die Kinder auch online – ohne das WLAN-Passwort zu kennen.

---

## Neu für die Kleinen (2–6 Jahre)

- **Startbildschirm der Kleinen** startet von selbst: große Kacheln, Programmname wird beim Antippen vorgelesen, eine Sonne zeigt die Restzeit.
- **Nur Programm und Haus:** Ein geöffnetes Programm füllt den ganzen Bildschirm, lässt sich nicht verkleinern; keine Taskleiste, kein Alt+Tab, keine Super-Taste, keine Bildschirmecken. Zurück geht es nur über den runden **🏠-Knopf** unten links.
- **Kein Weg in den Eltern-Bereich:** Auf dem Startbildschirm gibt es nur noch zwei Knöpfe – Herunterfahren und Abmelden. Kacheln richten die Eltern im Kontrollzentrum ein.
- **Jedes Programm nur einmal:** Zweimal antippen öffnet kein zweites Fenster, sondern holt das offene nach vorn.
- **Anmelden ohne Passwort** für die Kleinen: Profilbild antippen, fertig. Später im Kontrollzentrum umstellbar.

## Neu bei der Bildschirmzeit

- **Lernprogramme zählen nicht:** GCompris, Tux Paint, Malprogramme & Co. laufen nicht von der Zeit ab, Spiele, YouTube Kids und der Browser schon. Abschaltbar im Fenster „Bildschirmzeit“.
- **Restzeit in der Taskleiste** (ab 7 Jahren): „⏳ Noch 20 Min“ – grün, gelb, rot. Steht die Zeit gerade (nur Lernprogramme offen), wird das Feld blau: „🎨 zählt nicht“.
- **Fino erinnert** bei 15, 5 und 1 Minute Restzeit – vorgelesen, schließt sich von selbst.
- **„🙋 Mehr Zeit bitte“:** Das Kind bittet um 15 Minuten, Mama oder Papa geben mit dem Passwort frei.
- **Bildschirm-Pausen:** Nach 30–45 Minuten am Stück erinnert Fino ans Aufstehen. Abschaltbar.

## Neu im Kontrollzentrum (für Eltern)

- **Einrichtungs-Assistent** nach der Installation: Kinder anlegen, Filter wählen, Bildschirmzeit nach Alter – in einem Durchgang.
- **Nutzung:** Bildschirmzeit pro Kind für heute, gestern und die letzten 14 Tage, dazu die meistgenutzten Programme. Die Daten bleiben auf dem Rechner und löschen sich nach 30 Tagen.
- **Programme pro Kind:** Einzelne Programme trotz Alter erlauben oder trotz Alter sperren.
- **Kinderkonto zurücksetzen:** Einstellungen und Schreibtisch wie neu – Fotos und Dokumente bleiben.
- **YouTube Kids:** wahlweise frei oder nur mit Eltern-Passwort.
- **Hardware & Treiber:** zeigt Grafik, WLAN, Kernel und Secure Boot; Kernel-Wechsel auf Debian-Backports (und zurück) mit einem Klick, vorher automatische Sicherung.
- **Gestern wiederherstellen:** System mit einem Klick auf den Stand von gestern zurücksetzen.

## Neu bei Sicherung und Updates

- **Eigenes Paketarchiv** auf GitHub Pages, mit GPG unterschrieben. Ab Werk eingerichtet; die automatischen Updates holen Serafino mit.
- **Sicherungs-Stick sichert von selbst:** Nach der ersten Sicherung von Hand werden die eigenen Dateien bei jedem Einstecken gesichert.
- **USB-System-Sicherung mit Fortschritt** („34 %, noch etwa 5 Minuten“).

## App Store

- **108 Programme**, sortiert nach Kategorien, jedes mit Mindestalter. Kinder sehen nur, was für ihr Alter passt; Programme „nur für Eltern“ sind für Kinder unsichtbar und gesperrt.
- **Neu u. a.:** pySioGame, KolourPaint, Pinta, Pencil2D, Stopmotion, Elisa, GeoGebra, MuseScore, Laby, Minuet, KWordQuiz, Hex-a-Hop, Atomix, Hedgewars, GDevelop, Godot, VSCodium, Arduino IDE.
- **Nur für Eltern u. a.:** Virenscanner (ClamUI), Bottles, Synaptic, PDF Arranger, Calibre, KMyMoney, digiKam, KDE Partition Manager, Nextcloud, Syncthing, LocalSend, Bitwarden, Chrome, Brave.
- **Hinweis zu Chrome, Brave und anderen Browsern:** Unser Kinderschutz (Fino-Wächter, Sperrseiten, Werbeblocker) gilt nur im vorinstallierten Firefox. Andere Browser sind deshalb nur für Eltern.
- Chrome und VS Code kommen als **inoffizielle Flatpaks** von Flathub (proprietär, nicht vom Hersteller betreut) – das steht auch im Store dabei.

## Schutz und Sicherheit

- **WLAN für alle Kinderkonten:** Das WLAN der Eltern gilt automatisch für alle Konten. Kinder können das Passwort nicht anzeigen und die Verbindung nicht löschen.
- **Fino statt Fehlermeldung:** Gesperrte Programme, Terminal und gefilterte Webseiten zeigen Fino („Dafür brauchst du Mama oder Papa.“) statt einer technischen Meldung.
- **Wine für Kinder ganz gesperrt** – auch Bottles ist nur für Eltern.
- **Mikrofon** ist für Kinder unter 10 gesperrt, der Ton funktioniert trotzdem.
- **Serafino schützt sich selbst:** Das Serafino-Paket lässt sich weder mit `apt` noch mit Synaptic aus Versehen entfernen.

## Fino und Überraschungen

- **Fino durchs Jahr:** Hintergrundbilder für Winter, Ostern, Sommer und Herbst.
- **Geburtstag:** Am Geburtstag begrüßt Fino das Kind mit Partyhut und Konfetti.
- **Fino fliegt:** Im Kontrollzentrum 5× aufs Logo tippen.
- **Für Eltern im Terminal:** `serafino --fino` und `fastfetch` mit Fino-Logo.

## Behobene Fehler seit Beta 1

- Kein Ton im Kinderkonto auf dem Surface Go 2 (Mikrofon-Sperre hatte die ganze Soundkarte gesperrt).
- Emojis erschienen als leere Kästchen.
- Startbild beim Hochfahren (Plymouth) fehlte.
- YouTube Kids öffnete sich beim zweiten Antippen doppelt.
- YouTube Kids zählte nicht zur Bildschirmzeit.
- Leere Symbole in der Taskleiste für fehlende oder gesperrte Programme.
- Zurückwechseln vom Backports-Kernel auf den Debian-Kernel ging nicht.

---

## Experimentell

Diese Teile sind eingebaut, konnten aber mangels passender Hardware noch nicht vollständig getestet werden. **Rückmeldungen sind sehr willkommen.**

- **Hardware & Treiber – Nvidia-Treiber und Broadcom-WLAN:** Die Erkennung ist getestet (zwei Laptops mit GeForce-Grafik im Live-Modus), das Installieren der Treiber und der Secure-Boot-Ablauf (blauer MOK-Bildschirm) noch nicht.
- **Kernel-Wechsel (Backports):** getestet in der VM und auf dem Surface Go 2 mit Secure Boot – auf weiteren Geräten noch nicht.

---

## Datenschutz

Serafino sammelt keine Daten und schickt nichts ans Projekt. Welche Verbindungen ins Internet es gibt und wofür, steht im README unter „Datenschutz“.
