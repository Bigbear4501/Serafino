# Serafino 🐧

Ein kinderfreundliches Linux-System für Kinder von 2 bis 14 Jahren, basierend auf **Debian 13 („trixie“)** und **KDE Plasma**.
Maskottchen ist **Fino**, ein kleiner Pinguin mit Heiligenschein und Flügeln.

> ⚠️ **Status: Beta 2 – Testversion.** Bitte zum Ausprobieren nutzen, zum Beispiel in einer virtuellen Maschine oder auf einem Zweitgerät, **noch nicht als Alltags-PC für Kinder.**

## Was ist drin?

- **Oberfläche:** KDE Plasma im Serafino-Look (Fino im Startmenü, Eigener Ordner und Papierkorb auf dem Schreibtisch). Eignet sich auch für Tablets und Touch.
- **Anmeldebildschirm** (SDDM) mit Fino-Hintergrund und Profilbildern. Auf Touch-Geräten geht die Bildschirmtastatur beim Antippen des Passwortfelds von selbst auf, mit Maus und Tastatur bleibt sie zu.
- **Installer:** Calamares, auf Deutsch.
- **Eltern-Kontrollzentrum** mit großen Kacheln: Bildschirmzeit, Benutzerkonten, Konten-Übersicht, Nutzung, YouTube Kids, Startbildschirm der Kleinen, Kinderschutz-Filter, Firewall, App Store, Sicherung, Update-Assistent, Systembereinigung, Drucker und Scanner, Hardware & Treiber, Fehlerdiagnose und Hilfe. Kinder sehen es nicht. Alles, was Administrator-Rechte braucht, fragt nach dem Passwort eines Erwachsenen.
- **Eltern-Handbuch** direkt im System (Kontrollzentrum → Hilfe), auch ohne Internet: jede Kachel erklärt, dazu Fragen von Eltern (Passwort vergessen, Sicherung, Notfall).
- **Bildschirmzeit** in einem eigenen Fenster: heute genutzt und übrig, Extrazeit („+15 Min. heute“), Minuten pro Tag für Montag–Freitag und das Wochenende, erlaubte Uhrzeiten. Unterbau ist Timekpr-nExT.
- **Alter wächst mit:** Beim Anlegen eines Kinderkontos gibst du den Geburtstag an. Erlaubte Programme und Sperren passen sich an, wenn das Kind älter wird. Programme über der Altersgrenze erscheinen im Menü nicht.
- **Sperren pro Konto:** YouTube und soziale Netzwerke sind für Kinder unter 13 Jahren gesperrt, auch im privaten Fenster.
- **Kinderschutz-Filter (DNS):** CleanBrowsing Family (Standard) oder DNS4EU Kinderschutz. Kinder können ihn nicht umstellen.
- **Firewall** ab Werk eingeschaltet.
- **Browser:** Firefox mit kinderfreundlicher Startseite (fragFINN) und Kindersuchmaschine, Werbefilter (uBlock Origin) und dem **Fino-Wächter**: Gesperrte Seiten zeigen Fino statt einer Fehlermeldung. In der Lesezeichen-Leiste liegt der Ordner **„Schule“** (ANTON, Antolin, Microsoft Teams, Schulcloud, fragFINN). Eigene Erweiterungen lassen sich nicht installieren, `about:config` ist gesperrt.
- **YouTube Kids** im eigenen, abgeschotteten Fenster: kein Browser, keine Adressleiste, nur YouTube Kids. Die Bildschirmzeit begrenzt es wie jedes andere Programm.
- **Eigener, geprüfter App Store** mit Altersangabe pro Programm. Debian-Pakete haben Vorrang, Flatpak nur, wenn es kein Debian-Paket gibt. Programme lassen sich auch wieder entfernen.
- **Sicherung:**
  - das System **täglich von selbst** (Timeshift), dazu „System jetzt sichern“
  - **auf einen USB-Stick:** eigene Dateien aller Konten und auf Wunsch das System
  - **„Gestern wiederherstellen“**, falls nach einem Update etwas nicht mehr läuft
  - **Notfall:** Startet gar nichts mehr, lässt sich das System vom Serafino-Stick aus zurückholen
- **Updates:** Debian-Sicherheitsupdates und Programme aus dem App Store werden täglich von selbst installiert, vorher läuft die Sicherung. Der Update-Assistent hilft beim Wechsel auf eine neue Debian-Version.
- **Räumt selbst auf:** Einmal pro Woche verschwinden alte Kernel, nicht mehr gebrauchte Pakete und Download-Reste – mit Sicherheitsbremse, damit nie etwas Wichtiges entfernt wird.
- **Eltern-Passwort vergessen?** Ein zweites Eltern-Konto setzt es zurück, oder das Werkzeug „Eltern-Passwort zurücksetzen“ auf dem Serafino-Stick.
- **Lernen und Spielen:** GCompris, Tux Paint, Tux Typing, Tux Math, KTuberling, KLettres, KBruch, KGeography, Marble und mehr. Im App Store zusätzlich SuperTuxKart, Stellarium, Krita, Kalzium und weitere.
- **Büro und Alltag:** LibreOffice (im KDE-Stil), Marknote (Notizen), Crow Translate, Skanpage (Scannen), Kamoso (Kamera), Okular, Gwenview. Thunderbird gibt es im App Store.
- **Tablets:** Bildschirmdrehung, Touch und Bildschirmtastatur (nur Deutsch, ohne Autokorrektur).
- **Firmware** für gängige WLAN- und Grafikchips ist dabei, auch für ältere MacBooks (Broadcom).

## Neu in Beta 2

Alle Neuerungen stehen in den [Release Notes zu Beta 2](RELEASE-NOTES-BETA2.md). Das Wichtigste:

- **Eigener Startbildschirm für die Kleinen (2–6 Jahre):** große Kacheln, Namen werden vorgelesen, nur das Programm und ein Haus-Knopf – kein Weg in den Eltern-Bereich
- **Bildschirmzeit, die mitdenkt:** Lernprogramme zählen nicht, Spiele und Videos schon; „Mehr Zeit bitte“ mit Eltern-Passwort; Pausen-Erinnerung
- **Updates von selbst** über ein eigenes, signiertes Paketarchiv – neue Funktionen und Fehlerbehebungen ohne neue ISO
- **App Store mit 108 Programmen**, jedes mit Mindestalter
- **WLAN für alle Kinderkonten**, ohne dass die Kinder das WLAN-Passwort kennen
- **Neu im Kontrollzentrum:** Einrichtungs-Assistent, Nutzung pro Kind, Programme pro Kind, Kinderkonto zurücksetzen, Hardware & Treiber

## Download

> Die ISO ist rund 2,6 GB groß und liegt deshalb auf **SourceForge**, nicht in diesem Repository.

- **ISO-Download (Beta 2):** [serafino-beta2-amd64.iso](https://sourceforge.net/projects/pingulinux/files/Beta-2/serafino-beta2-amd64.iso/download) (SourceForge)
- **SHA256-Prüfsumme:**

```
70022e456853402219797d667a4824e24cb992521be8b4de2fcc934836a18040
```

Prüfsumme nach dem Download prüfen (im Ordner mit der ISO):

```bash
sha256sum serafino-beta2-amd64.iso
```

Die angezeigte Zahl muss mit der Prüfsumme oben übereinstimmen. Unter Windows: `certutil -hashfile serafino-beta2-amd64.iso SHA256`.

Ältere Versionen findest du auf [SourceForge](https://sourceforge.net/projects/pingulinux/files/).

## Ausprobieren

**Neu bei Linux?** Die **[Schritt-für-Schritt-Anleitung](INSTALLATION.md)** erklärt alles: ISO herunterladen, USB-Stick erstellen, vom Stick starten, Live-Modus und Installation. Es gibt sie auch [als PDF zum Ausdrucken](Serafino-Installationsanleitung.pdf).

Kurzfassung:

1. ISO herunterladen und Prüfsumme prüfen.
2. In einer virtuellen Maschine starten (z. B. GNOME Boxes, VirtualBox) oder mit einem Programm wie Balena Etcher auf einen USB-Stick schreiben.
3. Im **Live-Modus** ausprobieren. Dort braucht das Eltern-Kontrollzentrum kein Passwort. Das Passwort des Live-Kontos „Fino“ ist `live`. Flatpak-Programme lassen sich erst im installierten System installieren.
4. Zum Installieren das Symbol **„Serafino installieren“** benutzen. Das erste Konto ist das Eltern-Konto. Kinderkonten legst du danach im Kontrollzentrum unter „Benutzerkonten“ an.

**Getestet auf:** virtuellen Maschinen (GNOME Boxes), Microsoft Surface Go 2 (Touch, Secure Boot) und MacBook Air 2011/2012 (Live-Modus).

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
- **Firefox-Erweiterungen und Entwicklerwerkzeuge (F12)** sind ab Beta 3 für alle Konten gesperrt, auch für Eltern – sonst könnten Kinder den Kinderschutz mit einer Erweiterung umgehen. Erlaubt sind nur uBlock Origin und der Fino-Wächter.
- **Flatpaks** lassen sich nur im installierten System installieren, nicht im Live-Modus.
- **Platzhalter-Links:** Links für Datenschutz und Impressum fehlen noch. Wird bis 1.0 ergänzt.

## Fragen und Ideen

Du hast eine Frage zu Serafino, eine Idee oder möchtest zeigen, wie ihr es nutzt? Dafür gibt es die **[Diskussionen](../../discussions)** – ein Fragen-Bereich für Eltern. Bitte dort keine Namen oder Fotos von Kindern posten.

## Fehler melden

Bitte öffne ein [Issue](../../issues) (bei Unsicherheit gern erst in den [Diskussionen](../../discussions) fragen) und nenne dabei:

- Was hast du gemacht, und was ist passiert?
- Auf welchem Gerät (Modell, virtuelle Maschine oder echtes Gerät)?
- Live-Modus oder installiert?
- Den Bericht der **Fehlerdiagnose** aus dem Eltern-Kontrollzentrum (`Serafino-Diagnose.txt` im Eigenen Ordner), falls möglich.

## Aus den Quellen bauen

Serafino wird mit [live-build](https://wiki.debian.org/DebianLive) unter Debian 13 gebaut. Dieses Repository enthält die Konfiguration (`config/`) und das Bau-Skript (`rebuild.sh`).

```bash
sudo apt install live-build
git clone https://github.com/Bigbear4501/Serafino.git ~/kids-distro
cd ~/kids-distro
sudo lb clean
./rebuild.sh
```

Die fertige ISO liegt danach im Ordner `~/kids-distro`. Bei jedem Push prüft GitHub die Skripte automatisch auf Fehler (`.github/workflows/pruefung.yml`).

## Roadmap

### ✅ Beta 1
Nur noch KDE, neue Eltern-Fenster, Sicherung, automatische Updates, kleinere ISO.

### ✅ Beta 2 (aktuell)
Siehe „Neu in Beta 2“ oben und die [Release Notes](RELEASE-NOTES-BETA2.md).
- Noch offen: **Test mit echten Familien**

### Beta 3 (in Arbeit)
Fertig und per Update schon auf allen Beta-2-Rechnern:
- ✅ Umbenennung in **Serafino** mit Maskottchen **Fino** überall im System – Startbild, Boot-Menü, Anmeldung, Startmenü, Installer
- ✅ Ladebildschirm mit Fino beim Anmelden, nach dem Anmelden ist nichts mehr offen
- ✅ Einheitliche Passwort-Fenster („Bitte Mama oder Papa …“)
- ✅ Firefox: Lesezeichen „Schule“, eigene Erweiterungen gesperrt
- ✅ Wöchentliches Aufräumen mit Sicherheitsbremse
- ✅ Fragen-Bereich für Eltern ([Diskussionen](../../discussions))

Noch offen:
- WLAN schon im Installer verbinden
- Festplattenverschlüsselung und BitLocker-Hinweis prüfen und testen
- Nvidia- und Broadcom-Treiber auf echter Hardware testen
- Neue ISO

### 1.0
- ISO weiter verschlanken
- Rechtliches: Impressum, Datenschutz, Lizenzen
- Release-Prozess mit Prüfsummen, Signatur und Changelog
- Webseite

## Lizenz

Siehe die Datei `LICENSE`. Enthaltene Programme stehen unter ihren jeweiligen Lizenzen. Die Firmware-Pakete (`non-free-firmware`) sind nicht frei im Sinne der Debian-Richtlinien. Die mitgelieferte deutsche Übersetzung von Timekpr-nExT stammt aus dem Timekpr-nExT-Projekt (GPL-3).
