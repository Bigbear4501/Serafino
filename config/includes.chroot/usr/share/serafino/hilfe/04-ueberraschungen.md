# Überraschungen von Fino 🎉

Im System sind ein paar kleine Überraschungen versteckt. Für Kinder, damit sie etwas zu entdecken haben, und für Eltern, damit sie es ausprobieren und zeigen können.

## Fino fliegt vorbei

Im **Eltern-Kontrollzentrum** das Logo oben links **5-mal schnell** antippen oder anklicken.

Fino fliegt mit Flügelschlag über den Bildschirm, erzählt einen Witz in einer Sprechblase (und liest ihn vor) und fliegt wieder davon. Ein Klick irgendwo beendet ihn sofort.

## Fino im Terminal

Im Terminal (nur Eltern, Strg+Alt+T) eingeben:

```
serafino --fino
```

Fino erscheint als buntes Textbild und erzählt einen Witz. Bei jedem Aufruf ein anderer.

Wer nur `serafino` eingibt, bekommt einen kleinen Hinweis …

Fino zeigt sich auch hier, zusammen mit Infos zum Computer:

```
fastfetch
```

## Geburtstag

Bei der ersten Anmeldung am Geburtstag begrüßt Fino das Kind mit Partyhut, Konfetti und „Jetzt bist du 7! 🎉“ – vorgelesen. War das Kind am Geburtstag nicht am Computer, kommt der Gruß in den 14 Tagen danach. Einmal pro Jahr.

Ausprobieren, ohne auf den Geburtstag zu warten (im Terminal, die Zahl ist das Alter):

```
serafino-geburtstag.py --test 7
```

Den Gruß für dieses Jahr noch einmal sehen (im Konto des Kindes):

```
rm ~/.local/state/serafino/geburtstag-*
```

## Psst …

Verratet den Kindern nicht alles auf einmal – Fino freut sich, wenn er gefunden wird.
