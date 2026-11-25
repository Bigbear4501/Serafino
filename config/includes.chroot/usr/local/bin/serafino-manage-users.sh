#!/bin/bash
#
# serafino-manage-users.sh
#
# Einfache Benutzerverwaltung ohne sichtbares Terminal-Fenster.
# Neue Benutzer werden automatisch eingeschränkt angelegt: kein
# Admin-Konto (keine sudo-Gruppe) und ohne Zugriff auf den
# Terminal-Emulator.

# Dialog-Fenster (kdialog, sonst zenity) mit Serafino-Logo
. /usr/local/lib/serafino/dialog.sh
# Fragt nach einem Profilbild (Galerie). Gibt den Dateipfad aus (leer = Standardbild)
choose_avatar() {
    /usr/local/bin/serafino-pick-avatar.py "$1" 2>/dev/null
}
# Auswahl eines Benutzerkontos (Name wie im Anmeldebildschirm, dahinter der Benutzername)
pick_user() {
    local args=() u name
    while IFS=: read -r u _ uid _ gecos _; do
        [ "$uid" -ge 1000 ] && [ "$uid" -lt 60000 ] || continue
        name="${gecos%%,*}"
        args+=("$u" "${name:-$u} ($u)")
    done < <(getent passwd)
    pd_menue "$1" "Für wen?" "${args[@]}"
}

while true; do
    ACTION=$(pd_menue_ikon "Benutzerkonten verwalten" "Was möchtest du tun?" \
        "Neuen Benutzer anlegen" list-add "Neuen Benutzer anlegen" \
        "Profilbild ändern" edit-image "Profilbild ändern" \
        "Passwort ändern" dialog-password "Passwort ändern" \
        "Ohne Passwort" emblem-unlocked "Anmelden ohne Passwort (für die Kleinen) ein/aus" \
        "Programme" applications-other "Programme pro Kind (erlauben oder sperren, unabhängig vom Alter)" \
        "Zurücksetzen" edit-clear-history "Kinderkonto zurücksetzen (Einstellungen und Schreibtisch)" \
        "Benutzer löschen" edit-delete "Benutzer löschen")

    case "$ACTION" in
        "Neuen Benutzer anlegen")
            ANZEIGE=$(pd_eingabe "Neuer Benutzer" "Name des neuen Benutzerkontos (Groß- und Kleinschreibung egal):")
            if [ -z "$ANZEIGE" ]; then
                continue
            fi
            # Anmeldename ableiten: klein, ohne Umlaute/Sonderzeichen, eindeutig (Anna -> anna)
            anmeldename_aus() {
                local n="${1,,}" k i=2
                n="${n//ä/ae}"; n="${n//ö/oe}"; n="${n//ü/ue}"; n="${n//ß/ss}"; n="${n// /-}"
                n=$(printf '%s' "$n" | tr -cd 'a-z0-9_-' | sed 's/^[^a-z_]*//')
                n="${n:0:24}"; [ -n "$n" ] || n=kind
                k="$n"
                while id "$k" >/dev/null 2>&1; do k="$n$i"; i=$((i + 1)); done
                printf '%s' "$k"
            }
            NEWUSER=$(anmeldename_aus "$ANZEIGE")

            YNOW=$(date +%Y)
            YEARS=$(seq "$YNOW" -1 $((YNOW - 17)) | paste -sd'|')
            # Geburtstag: Tag → Monat → Jahr (drei kleine Auswahlfenster)
            # shellcheck disable=SC2046
            BDAY=$(pd_combo "Geburtstag von $ANZEIGE" "An welchem Tag hat $ANZEIGE Geburtstag?\nDas Alter bestimmt automatisch Bildschirmzeit und Schutzeinstellungen und wächst mit dem Kind mit – und Fino gratuliert am Geburtstag." "1" $(seq 1 31)) || continue
            case "$BDAY" in [1-9]|[12][0-9]|3[01]) ;; *) pd_fehler "Fehler" "Bitte den Tag auswählen."; continue;; esac
            BDAY=$(printf '%02d' "$BDAY")
            BMON_NAME=$(pd_combo "Geburtstag von $ANZEIGE" "In welchem Monat hat $ANZEIGE Geburtstag?" \
                "Januar" Januar Februar März April Mai Juni Juli August September Oktober November Dezember) || continue
            case "$BMON_NAME" in
                Januar) BMON=01;; Februar) BMON=02;; "März") BMON=03;; April) BMON=04;; Mai) BMON=05;; Juni) BMON=06;;
                Juli) BMON=07;; August) BMON=08;; September) BMON=09;; Oktober) BMON=10;; November) BMON=11;; Dezember) BMON=12;;
                *) pd_fehler "Fehler" "Bitte den Monat auswählen."; continue;;
            esac
            # shellcheck disable=SC2086
            BYEAR=$(pd_combo "Geburtstag von $ANZEIGE" "In welchem Jahr wurde $ANZEIGE geboren?" "$((YNOW - 6))" ${YEARS//|/ }) || continue
            case "$BYEAR" in [0-9][0-9][0-9][0-9]) ;; *) pd_fehler "Fehler" "Bitte das Jahr auswählen."; continue;; esac
            if ! date -d "$BYEAR-$BMON-$BDAY" >/dev/null 2>&1; then
                pd_fehler "Fehler" "Den $((10#$BDAY)). $BMON_NAME $BYEAR gibt es nicht. Bitte noch einmal."
                continue
            fi
            if [ "$(date -d "$BYEAR-$BMON-$BDAY" +%s)" -gt "$(date +%s)" ]; then
                pd_fehler "Fehler" "Dieser Geburtstag liegt in der Zukunft. Bitte noch einmal."
                continue
            fi
            BIRTH="$BYEAR-$BMON-$BDAY"
            AGE=$(/usr/local/bin/serafino-age-from-birth.sh "$BIRTH")

            # Für die Kleinen (bis 6): Anmelden ohne Passwort anbieten (bz21)
            MODUS=pw
            if [ "${AGE:-99}" -le 6 ] 2>/dev/null; then
                if pd_frage "Anmelden ohne Passwort?" "$ANZEIGE ist $AGE Jahre alt.\n\nSoll $ANZEIGE sich ohne Passwort anmelden können? Dann reicht ein Klick auf das Profilbild.\n\nAlle Sperren und die Bildschirmzeit gelten trotzdem. Später im Kontrollzentrum unter „Benutzerkonten“ umstellbar." "Ohne Passwort" "Mit Passwort"; then
                    MODUS=ohne
                fi
            fi
            PASS1=""
            if [ "$MODUS" = pw ]; then
                PASS1=$(pd_passwort "Neuer Benutzer" "Passwort für $ANZEIGE festlegen:")
                [ -z "$PASS1" ] && continue
                PASS2=$(pd_passwort "Neuer Benutzer" "Passwort wiederholen:")
                if [ "$PASS1" != "$PASS2" ]; then
                    pd_fehler "Fehler" "Die Passwörter stimmen nicht überein."
                    continue
                fi
            fi

            AVATAR=$(choose_avatar "$NEWUSER")

            if ERR=$(printf '%s' "$PASS1" | pkexec /usr/local/bin/serafino-root-helper konto-neu "$NEWUSER" "$BIRTH" "$AVATAR" "$MODUS" "$ANZEIGE" 2>&1); then
                if [ "$AGE" -lt 13 ]; then
                    SOCIAL="\n• Social-Media-Seiten und normales YouTube sind gesperrt (gilt nur für dieses Konto, im Firefox).\n• YouTube Kids liegt auf dem Desktop."
                else
                    SOCIAL=""
                fi
                [ "$MODUS" = ohne ] && OHNE="\n• Anmelden ohne Passwort: Klick auf das Profilbild genügt" || OHNE=""
                pd_info "Fertig" "Benutzerkonto '$ANZEIGE' wurde angelegt (Anmeldename: $NEWUSER).\n\n• Eingeschränktes Konto (kein Admin, kein Terminal)$OHNE\n• Bildschirmzeit automatisch passend für $AGE Jahre (wächst mit dem Kind mit)$SOCIAL\n\nDie Zeiten kannst du im Kontrollzentrum unter „Bildschirmzeit“ anpassen."
            else
                pd_fehler_roh "Fehler" "Das Benutzerkonto konnte nicht angelegt werden.

$ERR"
            fi
            ;;
        "Profilbild ändern")
            TARGET=$(pick_user "Profilbild ändern")
            if [ -n "$TARGET" ]; then
                IMG=$(choose_avatar "$TARGET")
                if [ -n "$IMG" ]; then
                    if pkexec /usr/local/bin/serafino-set-avatar.sh "$TARGET" "$IMG"; then
                        pd_info "Fertig" "Das Profilbild von '$TARGET' wurde geändert.\n\nBeim nächsten Anmelden ist es überall zu sehen."
                    else
                        pd_fehler "Fehler" "Das Profilbild konnte nicht geändert werden."
                    fi
                fi
            fi
            ;;
        "Passwort ändern")
            TARGET=$(pick_user "Passwort ändern")
            if [ -n "$TARGET" ]; then
                NEWPASS1=$(pd_passwort "Passwort ändern" "Neues Passwort für $TARGET:")
                if [ -z "$NEWPASS1" ]; then
                    continue
                fi
                NEWPASS2=$(pd_passwort "Neuer Benutzer" "Passwort wiederholen:")
                if [ "$NEWPASS1" != "$NEWPASS2" ]; then
                    pd_fehler "Fehler" "Die Passwörter stimmen nicht überein."
                    continue
                fi
                if ERR=$(printf '%s' "$NEWPASS1" | pkexec /usr/local/bin/serafino-set-password.sh "$TARGET" 2>&1); then
                    pd_info "Fertig" "Passwort für '$TARGET' wurde geändert."
                else
                    pd_fehler_roh "Fehler" "Das Passwort konnte nicht geändert werden.

$ERR"
                fi
            fi
            ;;
        "Ohne Passwort")
            # nur Kinderkonten (mit Alters-Profil, kein Admin) zur Auswahl
            args=()
            while IFS=: read -r u _ uid _ gecos _; do
                [ "$uid" -ge 1000 ] && [ "$uid" -lt 60000 ] || continue
                [ -f "/var/lib/serafino/profiles/$u" ] || continue
                id -nG "$u" | tr ' ' '\n' | grep -qx sudo && continue
                if id -nG "$u" | tr ' ' '\n' | grep -qx nopasswdlogin; then st="ohne Passwort"; else st="mit Passwort"; fi
                name="${gecos%%,*}"
                args+=("$u" "${name:-$u} ($u) – jetzt: $st")
            done < <(getent passwd)
            if [ ${#args[@]} -eq 0 ]; then
                pd_info "Anmelden ohne Passwort" "Es gibt noch kein Kinderkonto."
                continue
            fi
            TARGET=$(pd_menue "Anmelden ohne Passwort" "Für welches Kind?" "${args[@]}")
            [ -z "$TARGET" ] && continue
            if id -nG "$TARGET" | tr ' ' '\n' | grep -qx nopasswdlogin; then
                pd_frage "Wieder mit Passwort?" "$TARGET meldet sich im Moment ohne Passwort an.\n\nSoll $TARGET wieder ein Passwort brauchen? Du legst es gleich fest." "Passwort festlegen" "Abbrechen" || continue
                NEWPASS1=$(pd_passwort "Passwort für $TARGET" "Neues Passwort für $TARGET:")
                [ -z "$NEWPASS1" ] && continue
                NEWPASS2=$(pd_passwort "Passwort für $TARGET" "Passwort wiederholen:")
                if [ "$NEWPASS1" != "$NEWPASS2" ]; then
                    pd_fehler "Fehler" "Die Passwörter stimmen nicht überein."
                    continue
                fi
                if ERR=$(printf '%s' "$NEWPASS1" | pkexec /usr/local/bin/serafino-root-helper pw-mit "$TARGET" 2>&1); then
                    pd_info "Fertig" "$TARGET braucht ab der nächsten Anmeldung wieder das Passwort."
                else
                    pd_fehler_roh "Fehler" "Das hat nicht geklappt.

$ERR"
                fi
            else
                pd_frage "Ohne Passwort?" "Soll $TARGET sich ohne Passwort anmelden können?\n\nEmpfohlen für Kinder von 2 bis 6 Jahren. Jeder am Computer kann dann dieses Konto öffnen – alle Sperren und die Bildschirmzeit gelten trotzdem." "Ohne Passwort" "Abbrechen" || continue
                if ERR=$(pkexec /usr/local/bin/serafino-root-helper pw-los "$TARGET" 2>&1); then
                    pd_info "Fertig" "$TARGET meldet sich ab der nächsten Anmeldung ohne Passwort an: Profilbild anklicken, fertig."
                else
                    pd_fehler_roh "Fehler" "Das hat nicht geklappt.

$ERR"
                fi
            fi
            ;;
        "Programme")
            # bz3: einzelne Programme für ein Kind erlauben oder sperren
            /usr/local/bin/serafino-programme.py
            ;;
        "Zurücksetzen")
            # bz8: Einstellungen und Schreibtisch auf Anfang, eigene Dateien bleiben
            args=()
            while IFS=: read -r u _ uid _ gecos _; do
                [ "$uid" -ge 1000 ] && [ "$uid" -lt 60000 ] || continue
                [ -f "/var/lib/serafino/profiles/$u" ] || continue
                id -nG "$u" | tr ' ' '\n' | grep -qx sudo && continue
                name="${gecos%%,*}"
                args+=("$u" "${name:-$u} ($u)")
            done < <(getent passwd)
            if [ ${#args[@]} -eq 0 ]; then
                pd_info "Kinderkonto zurücksetzen" "Es gibt noch kein Kinderkonto."
                continue
            fi
            TARGET=$(pd_menue "Kinderkonto zurücksetzen" "Welches Konto?" "${args[@]}")
            [ -z "$TARGET" ] && continue
            pd_frage "Konto von $TARGET zurücksetzen?" "<b>Danach wie neu:</b> Einstellungen aller Programme, Schreibtisch, Firefox-Verlauf und Lesezeichen, Spielstände.\n\n<b>Bleibt erhalten:</b> Bilder, Dokumente, Musik, Videos, Downloads. Was auf dem Schreibtisch lag, kommt nach „Dokumente/Vom Schreibtisch“. Passwort, Alter und Bildschirmzeit bleiben auch.\n\nVorher wird alles gesichert. $TARGET muss dafür abgemeldet sein." "Zurücksetzen" "Abbrechen" || continue
            if ERR=$(pkexec /usr/local/bin/serafino-root-helper konto-reset "$TARGET" 2>&1); then
                pd_info "Fertig" "Das Konto von $TARGET ist zurückgesetzt. Beim nächsten Anmelden ist alles wie neu."
            else
                pd_fehler_roh "Nicht zurückgesetzt" "$(printf '%s' "$ERR" | tail -3)"
            fi
            ;;
        "Benutzer löschen")
            TARGET=$(pick_user "Benutzer löschen")
            if [ -n "$TARGET" ]; then
                if pd_frage "Wirklich löschen?" "Benutzer '$TARGET' mit allen eigenen Dateien wirklich löschen?" "Löschen" "Abbrechen"; then
                    if ERR=$(pkexec /usr/local/bin/serafino-delete-user.sh "$TARGET" 2>&1); then
                        pd_info "Fertig" "Benutzer '$TARGET' wurde gelöscht."
                    else
                        pd_fehler_roh "Fehler" "Der Benutzer konnte nicht gelöscht werden.

$ERR"
                    fi
                fi
            fi
            ;;
        *)
            break
            ;;
    esac
done
