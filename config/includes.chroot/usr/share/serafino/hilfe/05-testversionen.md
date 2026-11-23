# Mittesten – neue Versionen vor allen anderen

Neue Serafino-Versionen kommen zuerst in einen **Test-Bereich**. Dort laufen sie ein paar Tage auf den Rechnern von Testern. Erst wenn alles passt, bekommen alle Familien **genau diese Version** – unverändert, nicht neu gebaut.

> **Wichtig:** Testversionen können Fehler haben – genau dafür gibt es ja den Test. Schaltet den Test-Bereich nur auf einem Rechner ein, bei dem ein Fehler nicht schlimm wäre, und nicht auf dem einzigen Computer eurer Kinder.

## Einschalten

Es gibt dafür bewusst **keinen Knopf im Kontrollzentrum** – damit niemand ihn aus Versehen erwischt. Im Eltern-Konto eine Konsole öffnen (Startmenü → „Konsole“) und eingeben:

```
sudo serafino-testversionen an
```

Danach das Eltern-Passwort eingeben. Die nächste Testversion kommt mit den automatischen Updates – oder sofort mit:

```
sudo apt update && sudo apt upgrade
```

## Nachsehen, was eingestellt ist

```
serafino-testversionen status
```

Zeigt, ob der Test-Bereich an ist, welche Version installiert ist und woher sie kommt.

## Ausschalten

```
sudo serafino-testversionen aus
```

Eine schon installierte Testversion bleibt dabei erst einmal drauf. Sobald die nächste stabile Version erscheint, ersetzt sie die Testversion ganz normal – ihr müsst nichts weiter tun.

## Etwas gefunden?

Sagt uns Bescheid – im **Forum für Eltern** (Kontrollzentrum → Hilfe → „Fragen und Ideen“) oder als **Fehlermeldung** (Kontrollzentrum → Hilfe → „Fehler melden“). Am meisten hilft:

- welche Version installiert ist (`serafino-testversionen status`),
- was ihr gemacht habt und was dann passiert ist,
- der Bericht aus der **Fehlerdiagnose** im Kontrollzentrum.

Danke fürs Mittesten! 🐧
