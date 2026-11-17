# Pingulinux OS 🐧

Ein kinderfreundliches Linux-System für Kinder von 2 bis 14 Jahren, basierend auf **Debian 13 („trixie“)** und **KDE Plasma**.
Maskottchen ist **Pingu**, ein Pinguin mit grüner Kappe und Sonnenbrille.

> ⚠️ **Status: Beta 1 – Testversion.** Bitte zum Ausprobieren nutzen, zum Beispiel in einer virtuellen Maschine oder auf einem Zweitgerät, **noch nicht als Alltags-PC für Kinder.**
>
> **„Pingulinux“ ist ein Arbeitstitel.** Vor Version 1.0 wird der Name noch einmal geprüft und kann sich ändern. Das Projekt, die Funktionen und dieses Repository bleiben dabei bestehen.

## Was ist drin?

- **Oberfläche:** KDE Plasma im Pingulinux-Look (Pingu im Startmenü, Eigener Ordner und Papierkorb auf dem Schreibtisch). Eignet sich auch für Tablets und Touch.
- **Anmeldebildschirm** (SDDM) mit Pingu-Hintergrund und Profilbildern. Auf Touch-Geräten geht die Bildschirmtastatur beim Antippen des Passwortfelds von selbst auf, mit Maus und Tastatur bleibt sie zu.
- **Installer:** Calamares, auf Deutsch.
- **Eltern-Kontrollzentrum** mit großen Kacheln: Bildschirmzeit, Benutzerkonten, Konten-Übersicht, Kinderschutz-Filter, Firewall, App Store, Sicherung, Update-Assistent, Systembereinigung, Drucker und Scanner, Fehlerdiagnose und Hilfe. Kinder sehen es nicht. Alles, was Administrator-Rechte braucht, fragt nach dem Passwort eines Erwachsenen.
- **Eltern-Handbuch** direkt im System (Kontrollzentrum → Hilfe), auch ohne Internet: jede Kachel erklärt, dazu Fragen von Eltern (Passwort vergessen, Sicherung, Notfall).
- **Bildschirmzeit** in einem eigenen Fenster: heute genutzt und übrig, Extrazeit („+15 Min. heute“), Minuten pro Tag für Montag–Freitag und das Wochenende, erlaubte Uhrzeiten. Unterbau ist Timekpr-nExT.
- **Alter wächst mit:** Beim Anlegen eines Kinderkontos gibst du den Geburtstag an. Erlaubte Programme und Sperren passen sich an, wenn das Kind älter wird. Programme über der Altersgrenze erscheinen im Menü nicht.
- **Sperren pro Konto:** YouTube und soziale Netzwerke sind für Kinder unter 13 Jahren gesperrt, auch im privaten Fenster.
- **Kinderschutz-Filter (DNS):** CleanBrowsing Family (Standard) oder DNS4EU Kinderschutz. Kinder können ihn nicht umstellen.
- **Firewall** ab Werk eingeschaltet.
- **Browser:** Firefox mit kinderfreundlicher Startseite (fragFINN) und Kindersuchmaschine. `about:config` ist gesperrt.
- **YouTube Kids** im eigenen, abgeschotteten Fenster: kein Browser, keine Adressleiste, nur YouTube Kids. Die Bildschirmzeit begrenzt es wie jedes andere Programm.
- **Eigener, geprüfter App Store** mit Altersangabe pro Programm. Debian-Pakete haben Vorrang, Flatpak nur, wenn es kein Debian-Paket gibt. Programme lassen sich auch wieder entfernen.
- **Sicherung:**
  - das System **täglich von selbst** (Timeshift), dazu „System jetzt sichern“
  - **auf einen USB-Stick:** eigene Dateien aller Konten und auf Wunsch das System
  - **„Gestern wiederherstellen“**, falls nach einem Update etwas nicht mehr läuft
  - **Notfall:** Startet gar nichts mehr, lässt sich das System vom Pingulinux-Stick aus zurückholen
- **Updates:** Debian-Sicherheitsupdates und Programme aus dem App Store werden täglich von selbst installiert, vorher läuft die Sicherung. Der Update-Assistent hilft beim Wechsel auf eine neue Debian-Version.
- **Eltern-Passwort vergessen?** Ein zweites Eltern-Konto setzt es zurück, oder das Werkzeug „Eltern-Passwort zurücksetzen“ auf dem Pingulinux-Stick.
- **Lernen und Spielen:** GCompris, Tux Paint, Tux Typing, Tux Math, KTuberling, KLettres, KBruch, KGeography, Marble und mehr. Im App Store zusätzlich SuperTuxKart, Stellarium, Krita, Kalzium und weitere.
- **Büro und Alltag:** LibreOffice (im KDE-Stil), Marknote (Notizen), Crow Translate, Skanpage (Scannen), Kamoso (Kamera), Okular, Gwenview. Thunderbird gibt es im App Store.
- **Tablets:** Bildschirmdrehung, Touch und Bildschirmtastatur (nur Deutsch, ohne Autokorrektur).
- **Firmware** für gängige WLAN- und Grafikchips ist dabei, auch für ältere MacBooks (Broadcom).

## Neu in Beta 1

- **Nur noch KDE:** XFCE ist entfernt. Der letzte Stand mit XFCE bleibt im Zweig `xfce-light` erhalten.
- **Neue Eltern-Fenster im KDE-Stil:** Kontrollzentrum, Bildschirmzeit, Sicherung und Wiederherstellung, App Store und YouTube Kids
- **Sicherung:** täglich automatisch, auf USB-Stick, „Gestern wiederherstellen“ und Notfall-Rettung vom Stick
- **Automatische Updates** für Debian-Sicherheitsupdates und App-Store-Programme
- **Eltern-Handbuch** im System
- **Neuer Anmeldebildschirm (SDDM)** mit Bildschirmtastatur, die auf Touch-Geräten von selbst aufgeht
- **YouTube Kids ohne Eltern-Passwort**, begrenzt durch die Bildschirmzeit
- **Firewall** ab Werk an
- **Viel kleinere ISO:** rund 2,6 GB statt 4,2 GB (alte Pakete entfernt, Firmware bleibt)
- **Neue KDE-Programme:** Marknote, Crow Translate, Skanpage, Kamoso, KTuberling, KLettres, KBruch; einige größere Programme sind in den App Store gewandert
- **Behoben:** Passwort mit Zahlen im Installer per Bildschirmtastatur, Profilbild im Anmeldebildschirm, Live-Benutzer heißt „Pingu“, SuperTuxKart und KLettres auf Deutsch

## Download

> Die ISO ist rund 2,6 GB groß und liegt deshalb auf **SourceForge**, nicht in diesem Repository.

<!-- Nach dem Hochladen: Prüfsumme eintragen -->
- **ISO-Download (Beta 1):** [pingulinux-beta1-amd64.iso](https://sourceforge.net/projects/pingulinux/files/Beta-1/pingulinux-beta1-amd64.iso/download) (SourceForge)
- **SHA256-Prüfsumme:**

```
PRÜFSUMME-HIER-EINTRAGEN
```

Prüfsumme nach dem Download prüfen (im Ordner mit der ISO):

```bash
sha256sum pingulinux-beta1-amd64.iso
```

Die angezeigte Zahl muss mit der Prüfsumme oben übereinstimmen. Unter Windows: `certutil -hashfile pingulinux-beta1-amd64.iso SHA256`.

Ältere Versionen findest du auf [SourceForge](https://sourceforge.net/projects/pingulinux/files/).

## Ausprobieren

1. ISO herunterladen und Prüfsumme prüfen.
2. In einer virtuellen Maschine starten (z. B. GNOME Boxes, VirtualBox) oder mit einem Programm wie Balena Etcher auf einen USB-Stick schreiben.
3. Im **Live-Modus** ausprobieren. Dort braucht das Eltern-Kontrollzentrum kein Passwort. Das Passwort des Live-Kontos „Pingu“ ist `live`. Flatpak-Programme lassen sich erst im installierten System installieren.
4. Zum Installieren das Symbol **„Pingulinux OS installieren“** benutzen. Das erste Konto ist das Eltern-Konto. Kinderkonten legst du danach im Kontrollzentrum unter „Benutzerkonten“ an.

**Getestet auf:** virtuellen Maschinen (GNOME Boxes), Microsoft Surface Go 2 (Touch, Secure Boot) und MacBook Air 2011/2012 (Live-Modus).

## Bekannte Fehler (Beta 1)

| Fehler | Auswirkung | Geplant |
|---|---|---|
| Touch-Geräte ohne Tastatur: Die Suche im Startmenü mit der Bildschirmtastatur kann die Oberfläche einfrieren („plasmashell reagiert nicht“). Ursache ist ein Fehler in KDE. | Im Menü durchklicken oder mit einer echten Tastatur suchen. Falls es hängt: „Plasma beenden“ antippen, die Oberfläche startet von selbst neu. | Beta 2 |
| Auf manchen Geräten stimmen Uhrzeit oder Datum nicht. | Kann die Bildschirmzeit und Webseiten (Zertifikate) stören. Bitte melden, falls es bei dir auftritt. | Beta 2 |

## Datenschutz: Serafino sammelt keine Daten

Serafino schickt **nichts an uns**. Es gibt kein Konto, keine Werbung, keine Nutzungsstatistik und keine Absturzberichte an das Projekt. Alles, was Serafino über die Kinder weiß (Alter, Bildschirmzeit, die Übersicht „Nutzung“ im Kontrollzentrum), bleibt **auf dem Computer**. Eltern können es lesen, Kinder nicht. Die Nutzungs-Übersicht löscht Einträge, die älter als 30 Tage sind, von selbst.

Ganz ohne Internet geht es trotzdem nicht. Damit du genau weißt, wohin der Computer sich verbindet, steht hier jede Verbindung:

| Wohin | Wofür | Wann | Abschalten |
|---|---|---|---|
| Debian (`deb.debian.org`, `security.debian.org`) | Updates und Programme | täglich, und wenn im App Store etwas installiert wird | Updates abschalten ist nicht empfohlen |
| Serafino-Archiv auf GitHub Pages (`bigbear4501.github.io`) | Updates für die Serafino-Programme | täglich, zusammen mit den Debian-Updates | – |
| Flathub (`flathub.org`) | einige Programme aus dem App Store und deren Updates | nur wenn solche Programme installiert sind | Flathub-Programme wieder entfernen |
| Kinderschutz-Filter: CleanBrowsing oder DNS4EU | übersetzt Webadressen und blockiert ungeeignete Seiten. Der Dienst sieht dabei, **welche Seiten** aufgerufen werden, aber nicht, was darauf passiert. | bei jedem Seitenaufruf | Kontrollzentrum → Kinderschutz-Filter → Aus |
| Zeitserver (`debian.pool.ntp.org`) | richtige Uhrzeit (wichtig für die Bildschirmzeit) | beim Start und ab und zu | – |
| Firefox | Mozilla: Sperrlisten gegen gefährliche Seiten und Erweiterungs-Updates. uBlock Origin: Werbefilter-Listen. Die **Telemetrie ist abgeschaltet**. | wenn Firefox läuft | – |
| YouTube Kids (Google) | Videos | nur wenn YouTube Kids geöffnet ist. Es gelten die Regeln von Google. | Kontrollzentrum → YouTube Kids |
| fragFINN, Kindersuchmaschine | Startseite und Suche in Firefox | wenn Firefox geöffnet ist bzw. gesucht wird | in Firefox eine andere Startseite wählen |

Nur wenn Eltern es selbst starten oder installieren:

- **Fehlerdiagnose:** prüft mit einem einzelnen Ping an `1.1.1.1` (Cloudflare), ob Internet da ist. Der Bericht bleibt auf dem Computer.
- **Update-Assistent:** fragt bei Debian nach, ob es eine neue Debian-Version gibt.
- **Virenscanner (ClamUI), falls installiert:** lädt Virendaten von ClamAV.
- **Absturzmeldungen von KDE:** werden nur verschickt, wenn du sie selbst abschickst.

Wer eine Verbindung findet, die hier fehlt: bitte als [Issue](../../issues) melden.

## Bekannte Einschränkungen

- **Kinderschutz-Filter (DNS):** Nutzt einen externen DNS-Dienst (CleanBrowsing oder DNS4EU). Dabei werden DNS-Anfragen an diesen Dienst gesendet. Wer das nicht möchte, kann den Filter im Kontrollzentrum ausschalten.
- **`about:config`** ist in Firefox für alle Konten gesperrt, auch für Eltern. Normale Einstellungen gehen weiter über die Firefox-Einstellungen.
- **Flatpaks** lassen sich nur im installierten System installieren, nicht im Live-Modus.
- **Platzhalter-Links:** Links für Datenschutz und Impressum fehlen noch. Wird bis 1.0 ergänzt.

## Fehler melden

Bitte öffne ein [Issue](../../issues) und nenne dabei:

- Was hast du gemacht, und was ist passiert?
- Auf welchem Gerät (Modell, virtuelle Maschine oder echtes Gerät)?
- Live-Modus oder installiert?
- Den Bericht der **Fehlerdiagnose** aus dem Eltern-Kontrollzentrum (`Pingulinux-Diagnose.txt` im Eigenen Ordner), falls möglich.

## Aus den Quellen bauen

Pingulinux wird mit [live-build](https://wiki.debian.org/DebianLive) unter Debian 13 gebaut. Dieses Repository enthält die Konfiguration (`config/`) und das Bau-Skript (`rebuild.sh`).

```bash
sudo apt install live-build
git clone https://github.com/Bigbear4501/Pingulinux.git ~/kids-distro
cd ~/kids-distro
sudo lb clean
./rebuild.sh
```

Die fertige ISO liegt danach im Ordner `~/kids-distro`. Bei jedem Push prüft GitHub die Skripte automatisch auf Fehler (`.github/workflows/pruefung.yml`).

## Roadmap

### ✅ Beta 1 (aktuell)
Siehe „Neu in Beta 1“ oben.

### Beta 2: Praxis und Feinschliff
- **Test mit echten Familien**
- **Sicherung der eigenen Dateien automatisch**, sobald der Sicherungs-Stick eingesteckt ist
- **Kinderkonten ohne Passwort** für die Kleinen (2–6 Jahre)
- **Treiber-Assistent** für Grafik- und WLAN-Treiber, wie bei Ubuntu
- **Fortschrittsanzeige** bei der System-Sicherung
- **Alle bekannten Fehler beheben**, auch die aus dem Familientest

### Beta 3
- Festplattenverschlüsselung prüfen und testen
- Feinschliff aus Beta 2

### 1.0
- Name endgültig festlegen
- ISO weiter verschlanken
- Rechtliches: Impressum, Datenschutz, Lizenzen
- Release-Prozess mit Prüfsummen, Signatur und Changelog
- Webseite und Eltern-Handbuch als PDF

## Lizenz

Siehe die Datei `LICENSE`. Enthaltene Programme stehen unter ihren jeweiligen Lizenzen. Die Firmware-Pakete (`non-free-firmware`) sind nicht frei im Sinne der Debian-Richtlinien. Die mitgelieferte deutsche Übersetzung von Timekpr-nExT stammt aus dem Timekpr-nExT-Projekt (GPL-3).
