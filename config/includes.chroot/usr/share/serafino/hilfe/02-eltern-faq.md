# Serafino – Fragen von Eltern

Kurze Antworten auf häufige Fragen. Diese Seite wächst mit der Zeit.

---

## Ich habe mein Eltern-Passwort vergessen. Was jetzt?

Keine Sorge, die Kinderkonten, Fotos und Dokumente bleiben erhalten. Es gibt zwei Wege.

### Weg 1: Ein anderes Eltern-Konto setzt das Passwort neu

Am einfachsten geht es, wenn es auf dem Computer **zwei Eltern-Konten** gibt, zum Beispiel eins für Mama und eins für Papa.

1. Mit dem anderen Eltern-Konto anmelden.
2. Das **Eltern-Kontrollzentrum** öffnen (Symbol auf dem Schreibtisch).
3. **Benutzerkonten** wählen, das Konto mit dem vergessenen Passwort auswählen und ein neues Passwort vergeben.

> **Tipp:** Legt gleich nach der Installation für beide Eltern ein eigenes Konto mit Eltern-Rechten an. Dann braucht ihr Weg 2 nie.

### Weg 2: Mit dem Serafino-Stick zurücksetzen

Wenn es nur ein Eltern-Konto gibt:

1. Den **Serafino-USB-Stick** einstecken (der Stick, mit dem Serafino installiert wurde, oder ein neu erstellter).
2. Den Computer vom Stick starten. Serafino startet im Live-Modus.
3. Im **Startmenü** unter **System** auf **„Eltern-Passwort zurücksetzen“** klicken.
4. Das Werkzeug findet das installierte Serafino von selbst. Das Eltern-Konto auswählen und zweimal das neue Passwort eingeben.
5. Stick abziehen und den Computer neu starten. Jetzt gilt das neue Passwort.

**Gut zu wissen:** Bei einer **verschlüsselten Festplatte** funktioniert Weg 2 nicht.

---

## Kann mein Kind den Stick-Trick auch benutzen?

Wer den Computer vom USB-Stick starten kann, kommt an alles auf der Festplatte heran. Das gilt für jedes Betriebssystem, nicht nur für Serafino. Deshalb:

- Im **BIOS/UEFI** ein Passwort setzen.
- Dort den **Start vom USB-Stick abschalten** (oder nur mit Passwort erlauben).
- Den Serafino-Stick nicht beim Computer liegen lassen.

Braucht ihr den Stick später selbst (Weg 2), schaltet ihr den USB-Start mit eurem BIOS-Passwort kurz wieder ein.

Wie man ins BIOS kommt, hängt vom Gerät ab. Meist hilft beim Einschalten eine der Tasten **F2**, **Entf**, **F10** oder **Esc**.

---

## Wie sichert Serafino unsere Daten?

### Automatisch: das System, jeden Tag

Serafino sichert das **System** einmal am Tag von selbst (mit Timeshift) und behält die letzten 5 Stände. Diese Sicherung liegt auf derselben Festplatte. Sie hilft, wenn nach einem Update oder einer Einstellung etwas nicht mehr läuft – nicht aber, wenn die Festplatte kaputtgeht.

**Nicht** automatisch gesichert werden die **eigenen Dateien** (Fotos, Dokumente, Spielstände). Dafür gibt es die Sicherung auf einen USB-Stick.

### Von Hand: auf einen USB-Stick oder eine USB-Platte

1. Stick oder USB-Platte einstecken.
2. **Eltern-Kontrollzentrum → Sicherung und Wiederherstellung → Auf USB-Stick sichern**.
3. Stick auswählen und festlegen, was drauf soll: **Eigene Dateien** und/oder **System**.
4. Passwort eingeben – die Sicherung läuft durch. Danach „Stick auswerfen“.

**Gut zu wissen:**
- Eigene Dateien gehen auf jeden Stick. Auf dem Stick wird nie etwas gelöscht: Was zu Hause gelöscht wurde, bleibt auf dem Stick erhalten.
- Für die **System-Sicherung** braucht der Stick das Linux-Format (ext4). Serafino bietet an, den Stick dafür zu formatieren – **dabei wird alles auf dem Stick gelöscht**, und Windows kann ihn danach nicht mehr lesen. Am besten einen eigenen Stick nur für die Sicherung nehmen.
- Wer es regelmäßig macht (z. B. einmal im Monat), ist auch bei einer kaputten Festplatte auf der sicheren Seite.

### Zurückholen

- **Eigene Dateien:** Kontrollzentrum → Sicherung und Wiederherstellung → „Eigene Dateien vom Stick zurückholen“. Der Dateimanager öffnet sich; die Dateien liegen unter *Serafino-Sicherung → Name des Computers → Eigene-Dateien* und lassen sich einfach zurückkopieren.
- **System:** Kontrollzentrum → Sicherung und Wiederherstellung → „System wiederherstellen“. Dort einen Stand auswählen – auch einen vom Stick, wenn er eingesteckt ist.

### Serafino startet gar nicht mehr – was jetzt?

Auch dann lässt sich eine Sicherung zurückspielen:

1. Den **Serafino-USB-Stick** einstecken und den Computer davon starten (Live-Modus).
2. Im Startmenü unter **System** auf **„System retten (Timeshift)“** klicken.
3. Timeshift fragt, wo die Sicherungen liegen: die **eingebaute Festplatte** wählen (oder den Sicherungs-Stick, falls die Festplatte kaputt ist).
4. Einen Stand auswählen, auf **„Wiederherstellen“** klicken und den Anweisungen folgen. Als Ziel die eingebaute Festplatte nehmen.
5. Stick abziehen, neu starten.

Die eigenen Dateien (Fotos, Dokumente) bleiben dabei unverändert. Ist die Festplatte selbst kaputt, hilft nur noch die Sicherung auf dem USB-Stick – deshalb ab und zu „Auf USB-Stick sichern“.

## Braucht Serafino einen Virenscanner?

Für den Alltag nicht: Kinder können keine heruntergeladenen Programme starten, und der Filter sperrt gefährliche Seiten. Wer aber USB-Sticks oder Dateien für Windows-Rechner prüfen will, kann im **App Store** unter *Dienstprogramme* den **Virenscanner (ClamUI)** installieren.

- Er ist **nur für Eltern** sichtbar – in Kinderkonten taucht er weder im App Store noch im Startmenü auf.
- Er läuft **nicht im Hintergrund**. Geprüft wird nur, wenn Sie ClamUI öffnen und einen Ordner oder Stick auswählen.
- Die Installation dauert einige Minuten, weil beim ersten Mal die Virendaten (etwa 200 MB) geladen werden. Danach holt Serafino nichts von selbst: Neue Virendaten gibt es, wenn Sie ClamUI öffnen und dort die Virendaten aktualisieren – am besten jedes Mal vor dem Prüfen.
- Entfernen geht wie bei jedem Programm im App Store; dabei werden auch ClamAV und die Virendaten gelöscht.

---

## Wie füge ich die Seite unserer Schule (z. B. Moodle) hinzu?

Den Ordner **„Schule“** in der Lesezeichen-Leiste legt Serafino fest an. Eigene Seiten kommen so dazu:

1. Die Seite in Firefox öffnen, zum Beispiel die Moodle-Seite eurer Schule.
2. Auf den **Stern** rechts in der Adressleiste klicken.
3. Bei „Ordner“ **„Lesezeichen-Symbolleiste“** wählen und „Fertig“ klicken.

Das geht im Konto des Kindes – am besten zusammen mit dem Kind, damit es die Seite wiederfindet.

## Warum kann ich in Firefox keine Erweiterung installieren?

Mit einer Erweiterung, zum Beispiel einem VPN oder Proxy, ließe sich der Kinderschutz umgehen. Firefox kennt solche Sperren nur für alle Konten gemeinsam, deshalb gilt sie auch für Eltern. Fest eingebaut sind der Werbefilter **uBlock Origin** und der **Fino-Wächter**. Fehlt euch eine Erweiterung wirklich, schreibt uns im Forum („Fragen und Ideen“).

## Wird die Festplatte mit der Zeit voll?

Nein, Serafino räumt einmal pro Woche selbst auf: alte Kernel, nicht mehr gebrauchte Pakete und Download-Reste. Eigene Dateien, Fotos und Spielstände fasst es dabei nie an. Mehr dazu im Kontrollzentrum unter „Systembereinigung“.

## Wo kann ich Fragen stellen?

Im **Forum für Eltern**: Kontrollzentrum → Hilfe → „Fragen und Ideen (Forum für Eltern)“. Dort antworten wir und andere Eltern. Bitte keine Namen oder Fotos von Kindern posten – das Forum ist öffentlich. Einen Fehler gefunden? Dann unter Hilfe → „Fehler melden“, am besten mit dem Bericht der Fehlerdiagnose.

## Der Installer warnt vor „BitLocker“ – was heißt das?

BitLocker ist die Festplatten-Verschlüsselung von Windows. Viele neuere Laptops haben sie eingeschaltet, ohne dass man es merkt.

- **Ihr löscht bei der Installation die ganze Festplatte:** Dann ist die Warnung egal, einfach „Weiter“.
- **Ihr wollt Windows behalten:** Dann zuerst abbrechen, Windows starten und den **Wiederherstellungsschlüssel** sichern: im Browser **aka.ms/myrecoverykey** öffnen und mit dem Microsoft-Konto anmelden. Den 48-stelligen Schlüssel aufschreiben oder ausdrucken. Am sichersten ist es, BitLocker vorher auszuschalten: Windows-Suche → „BitLocker verwalten“ → „BitLocker deaktivieren“ (Windows Home: Einstellungen → Datenschutz und Sicherheit → Geräteverschlüsselung → Aus). Danach wieder vom Serafino-Stick starten.

Fragt Windows nach der Installation trotzdem nach dem Schlüssel, gebt ihr ihn einmal ein – danach startet Windows wieder normal.

## Kann ich die Festplatte verschlüsseln?

Serafino bietet das bei der Installation bewusst **nicht** an, und wir empfehlen es für einen Familien-Computer auch nicht. Bei einer verschlüsselten Festplatte muss bei jedem Einschalten ein zusätzliches Passwort eingegeben werden – das kann kein Kind allein, und wer das Passwort vergisst, kommt nie wieder an Fotos, Dokumente und Spielstände heran. Wichtiger als Verschlüsselung sind gute Passwörter für die Eltern-Konten und regelmäßige Sicherungen (Kontrollzentrum → Sicherung).
