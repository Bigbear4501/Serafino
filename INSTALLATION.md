# Serafino installieren – Schritt für Schritt

Diese Anleitung führt dich vom Herunterladen bis zum ersten Anmelden. Du brauchst keine Linux-Kenntnisse. Plane etwa **eine Stunde** ein, davon wartest du die meiste Zeit.

> ⚠️ **Serafino ist noch eine Beta (Testversion).** Probiere es am besten auf einem Zweitgerät aus, zum Beispiel einem älteren Laptop. Bei der Installation wird die Festplatte des Computers **komplett gelöscht** – Windows und alle Dateien darauf sind danach weg.

---

## 1. Was du brauchst

- **Einen Computer oder Laptop**, auf dem Serafino laufen soll:
    - 64-Bit-Prozessor (Intel oder AMD, fast alle Geräte ab etwa 2010)
    - mindestens **4 GB Arbeitsspeicher**, besser 8 GB
    - mindestens **32 GB Festplatte**
- **Einen USB-Stick mit mindestens 8 GB.** Alles, was darauf liegt, wird gelöscht.
- **Einen zweiten Computer** mit Internet, um den Stick vorzubereiten (Windows, Mac oder Linux). Das kann auch derselbe sein, solange dort noch das alte System läuft.
- **Internet** (WLAN oder Kabel) – für Updates und den App Store.

**Läuft auf dem Computer Windows mit BitLocker?** Viele neuere Laptops verschlüsseln die Festplatte von Haus aus. Der Serafino-Installer merkt das und warnt dich.

- **Du löschst die ganze Festplatte** (empfohlen): Dann musst du nichts tun – Windows ist danach ohnehin weg.
- **Du willst Windows behalten:** Dann vorher in Windows den **Wiederherstellungsschlüssel aufschreiben** – im Browser **aka.ms/myrecoverykey** öffnen und mit dem Microsoft-Konto anmelden. Am besten schaltest du BitLocker außerdem aus: Windows-Suche → „BitLocker verwalten“ → „BitLocker deaktivieren“ (bei Windows Home: Einstellungen → Datenschutz und Sicherheit → Geräteverschlüsselung → Aus) und wartest, bis Windows fertig ist. Ohne Schlüssel kann es passieren, dass Windows nach der Installation nicht mehr startet.

**Vorher sichern:** Liegen auf dem Computer noch Fotos oder Dokumente, die du behalten willst? Dann kopiere sie jetzt auf eine externe Festplatte oder einen anderen Stick.

---

## 2. Serafino herunterladen

1. Öffne die Download-Seite: **[Serafino auf SourceForge](https://sourceforge.net/projects/pingulinux/files/)** und wähle die neueste Version (zum Beispiel `Beta-2` → `serafino-beta2-amd64.iso`).
2. Der Download startet von selbst. Die Datei ist rund **2,7 GB** groß – das kann je nach Internet eine Weile dauern.

Die Datei endet auf **`.iso`**. Das ist ein „Abbild“ des ganzen Systems – du kannst sie nicht einfach doppelklicken, sondern schreibst sie gleich auf den USB-Stick.

### Prüfen, ob der Download vollständig ist (empfohlen)

Im README steht bei jeder Version eine **Prüfsumme** – eine lange Zeichenkette aus Zahlen und Buchstaben. Ist die Datei beim Herunterladen beschädigt worden, stimmt sie nicht.

- **Windows:** Im Ordner „Downloads“ mit der rechten Maustaste auf eine freie Stelle → „Im Terminal öffnen“, dann eingeben:
  `certutil -hashfile serafino-beta2-amd64.iso SHA256`
- **Mac:** Programm „Terminal“ öffnen und eingeben:
  `shasum -a 256 ~/Downloads/serafino-beta2-amd64.iso`
- **Linux:** `sha256sum ~/Downloads/serafino-beta2-amd64.iso`

Vergleiche die angezeigte Zeichenkette mit der im README. Stimmt sie überein, ist alles gut. Weicht sie ab: Datei löschen und noch einmal herunterladen.

**Für Fortgeschrittene – Unterschrift prüfen (Linux):** Neben der ISO liegen `SHA256SUMS`, die Unterschrift `SHA256SUMS.asc` und der öffentliche Schlüssel `serafino-archiv.asc`. Alle in einen Ordner laden, dann:
`gpg --import serafino-archiv.asc && gpg --verify SHA256SUMS.asc SHA256SUMS && sha256sum -c SHA256SUMS`
Erwartet: „Korrekte Signatur von Serafino Paketarchiv“ und „OK“. Der Fingerabdruck des Schlüssels ist `C207 1895 9362 B2F8 A3F1 E3D5 13C8 8339 3569 CB29`.

---

## 3. Den USB-Stick erstellen

Am einfachsten geht das mit dem kostenlosen Programm **balenaEtcher** – es läuft auf Windows, Mac und Linux und macht kaum etwas falsch.

1. **balenaEtcher** von [etcher.balena.io](https://etcher.balena.io) herunterladen und installieren.
2. USB-Stick einstecken.
3. Etcher öffnen:
    - **„Flash from file“** → die heruntergeladene `serafino-…-amd64.iso` auswählen.
    - **„Select target“** → den USB-Stick auswählen. **Genau hinschauen**, dass es wirklich der Stick ist und nicht eine externe Festplatte!
    - **„Flash!“** klicken. Windows und Mac fragen eventuell nach deinem Passwort.
4. Nach ein paar Minuten meldet Etcher **„Flash Complete!“**. Fertig.

**Windows meldet danach „Sie müssen den Datenträger formatieren“?** Auf **„Abbrechen“** klicken! Windows kann den Stick nur nicht lesen – das ist normal. Formatieren würde den Stick wieder löschen.

**Alternative für Windows: Rufus** ([rufus.ie](https://rufus.ie)). Stick und ISO auswählen, „Start“. Fragt Rufus nach dem Modus, **„Im DD-Abbild-Modus schreiben“** wählen.

---

## 4. Den Computer vom Stick starten

Jetzt kommt der Computer an die Reihe, auf dem Serafino laufen soll. Normalerweise startet er sein eingebautes System (zum Beispiel Windows). Damit er stattdessen vom Stick startet, öffnest du beim Einschalten das **Startmenü des Computers** (Boot-Menü).

1. Computer **ganz ausschalten**, den Stick einstecken (am besten direkt am Gerät, nicht über einen Verteiler).
2. Einschalten und **sofort mehrmals** die Taste für das Boot-Menü drücken:

| Hersteller | Taste |
|---|---|
| Lenovo | **F12** (manche Laptops: kleiner Knopf mit Pfeil an der Seite) |
| Dell | **F12** |
| HP | **F9** (oder **Esc**, dann F9) |
| Acer | **F12** |
| ASUS | **Esc** oder **F8** |
| MSI | **F11** |
| Medion | **F10** |
| Microsoft Surface | **Lautstärke leiser** gedrückt halten, dann Einschaltknopf kurz drücken, Lautstärketaste festhalten, bis das Surface-Logo kommt |
| Apple Mac (Intel) | **Alt / Option** gedrückt halten |

3. Im Boot-Menü den **USB-Stick** auswählen (er heißt oft „USB“, „UEFI: …“ oder nach dem Hersteller des Sticks) und mit Enter bestätigen.

**Es klappt nicht?**

- **Windows startet trotzdem:** Windows fährt manchmal nicht richtig herunter („Schnellstart“). Dann in Windows auf Start → Ein/Aus klicken und **mit gedrückter Umschalttaste (⇧) auf „Neu starten“** klicken. Im blauen Menü **„Gerät verwenden“** wählen und dort den USB-Stick.
- **Der Stick taucht nicht auf:** einen anderen USB-Anschluss probieren, den Stick neu erstellen (Schritt 3) oder im BIOS/UEFI nachsehen, ob der Start von USB erlaubt ist.
- **Secure Boot** musst du **nicht** abschalten – Serafino startet auch mit Secure Boot.

---

## 5. Der Live-Modus: erst einmal ausprobieren

Nach dem Start vom Stick erscheint ein kleines Menü – einfach warten oder Enter drücken. Kurz darauf siehst du den Serafino-Schreibtisch mit Fino.

Das ist der **Live-Modus**: Serafino läuft komplett **vom USB-Stick**. Am Computer wird **nichts verändert** – die Festplatte bleibt, wie sie ist. Alles, was du jetzt tust, ist nach dem Ausschalten wieder weg.

Der Live-Modus ist ideal, um zu prüfen, ob Serafino auf dem Gerät gut läuft:

- **WLAN:** Unten rechts auf das Netzwerk-Symbol klicken und mit dem WLAN verbinden.
- **Ton:** Ein Video oder YouTube Kids abspielen.
- **Bildschirm und Touch:** Stimmt die Auflösung? Funktioniert Touch, falls vorhanden?
- **Eltern-Kontrollzentrum** und **App Store** anschauen.

**Gut zu wissen:**

- Das Live-Konto heißt **„Fino“**, das Passwort ist **`live`** (falls es einmal gefragt wird).
- Im Live-Modus fragt das Kontrollzentrum nicht nach einem Passwort.
- Programme aus dem App Store, die als „Flatpak“ kommen, lassen sich erst nach der Installation installieren.
- Vom Stick läuft alles etwas langsamer als später von der Festplatte.

Läuft alles? Dann geht es weiter mit der Installation.

---

## 6. Serafino installieren

> ⚠️ **Letzte Warnung:** Bei der Installation wird die Festplatte **komplett gelöscht**. Sind alle wichtigen Dateien gesichert?

Doppelklicke auf dem Schreibtisch auf **„Serafino installieren“**. Der Installer führt dich in wenigen Schritten durch:

1. **Willkommen:** Sprache **Deutsch** ist schon ausgewählt → „Weiter“.
2. **Standort:** Region und Zeitzone (z. B. **Europa / Berlin**) → „Weiter“.
3. **Tastatur:** **Deutsch** ist voreingestellt. Im Feld darunter kannst du testen, ob ä, ö, ü und ß richtig kommen → „Weiter“.
4. **Partitionen** (wohin Serafino installiert wird):
    - Die richtige Festplatte auswählen (meist gibt es nur eine).
    - **„Festplatte löschen“** wählen. Das ist der einfachste und sicherste Weg.
    - „Neben Windows installieren“ (Dual Boot) ist möglich – der Installer kommt von Debian und kann das. **Wir testen es aber nicht selbst.** Wer Windows behalten will: vorher alles sichern und bei BitLocker den Wiederherstellungsschlüssel bereithalten (siehe Schritt 1). Die Kinderschutz-Sperren gelten nur in Serafino, nicht in Windows.
   → „Weiter“.
5. **Benutzer:** Hier legst du das **Eltern-Konto** an – das ist dein Konto, nicht das der Kinder.
    - Dein Name, ein Anmeldename (z. B. `mama` oder `papa`) und der Name des Computers.
    - Ein **gutes Passwort**, das die Kinder nicht kennen. Dieses Passwort brauchst du später für alles, was Kinder nicht dürfen.
    - „Automatisch anmelden“ **nicht** anhaken – sonst landet jeder, der den Computer einschaltet, direkt im Eltern-Konto.
   → „Weiter“.
6. **Zusammenfassung:** Noch einmal prüfen → **„Installieren“** → bestätigen.
7. Die Installation dauert etwa **10 bis 20 Minuten**. Den Laptop dabei **am Strom lassen**.
8. **Fertig:** Haken bei „Jetzt neu starten“ lassen → „Erledigt“. **Den USB-Stick abziehen**, sobald der Bildschirm schwarz wird.

---

## 7. Der erste Start

1. Serafino startet mit Fino und dem Anmeldebildschirm. Melde dich mit deinem **Eltern-Konto** an.
2. **Mit dem Internet verbinden** (unten rechts das Netzwerk-Symbol). Das WLAN gilt danach automatisch auch für alle Kinderkonten – die Kinder müssen das WLAN-Passwort nicht kennen.
3. Der **Einrichtungs-Assistent** öffnet sich von selbst und hilft in drei Schritten:
    - **Kinderkonten anlegen** – mit Vornamen und Geburtstag. Das Alter wächst dann automatisch mit.
    - **Kinderschutz-Filter** wählen (CleanBrowsing ist voreingestellt).
    - **Bildschirmzeit** festlegen – Serafino schlägt passende Zeiten fürs Alter vor.

    Am Ende einmal das Eltern-Passwort eingeben, fertig.
4. **Updates** laufen ab jetzt jeden Tag von selbst, vorher sichert Serafino das System.

**Tipps für den Anfang:**

- Lege im Kontrollzentrum unter **Benutzerkonten** ein **zweites Eltern-Konto** an (für den anderen Elternteil). Dann kann einer dem anderen helfen, falls ein Passwort vergessen wird.
- Bewahre den **USB-Stick** gut auf – mit ihm kannst du im Notfall das Eltern-Passwort zurücksetzen oder das System retten. Aber nicht so, dass die Kinder ihn finden.
- Wer ganz sicher gehen will, setzt im **BIOS/UEFI ein Passwort** und schaltet den Start vom USB-Stick ab. Mehr dazu im Eltern-Handbuch unter „Kann mein Kind den Stick-Trick auch benutzen?“.
- Alles Weitere steht im **Eltern-Handbuch**: Kontrollzentrum → Hilfe.

---

## Hilfe gesucht?

- **Fragen** – Kontrollzentrum → Hilfe → „Fragen und Ideen (Forum für Eltern)“, oder direkt im [Forum für Eltern](https://github.com/Bigbear4501/Serafino/discussions).
- **Fehler gefunden** – bitte als [Issue](https://github.com/Bigbear4501/Serafino/issues) melden, am besten mit dem Bericht der **Fehlerdiagnose** (Kontrollzentrum → Fehlerdiagnose).
