# Server-Script für den "OG Racer"

## Installation

Socket.IO und eventlet sind dependencies. Achtet darauf das ihr das Package python-socketio und nicht socketio ladet. In der Regel müsst ihr euch aber um garnix kümmern, da ein venv beigelegt ist.

- Klone das Repo
- Stelle sicher das du das beigefügte venv nutzt
    - dazu in das Verzeichnis wechseln und folgenden Befehl nutzen "python -m pm_server_env" oder nötige Konfiguration in IDE vornehmen
- main.py ausführen

**WICHTIG:** Aktuell läuft der Server über den Localhost, das heißt nur lokale Anfragen werden bearbeitet. Möchtet ihr versuchen das ganze Online laufen zu lassen so müsst ihr die IP von localhost zu 0.0.0.0 ändern. Beachtet aber auch Portfreigaben in Firewalls/Routern. So wie die Tatsache das ihr euch damit in der aktuellen Version, mit ziemlich hoher Sicherheit (100%), eine Tür für jeden böswilligen Netzwerkteilnehmer aufmacht.

## Interagieren mit dem Server


### Login

Für den Login sendet ihr ein JSON über das event **'login'** an den Server, das JSON muss die keys **'user'** und **'password'** besitzen, in welchem die Eingaben des Benutzers sind.

Der Server wird daraufhin prüfen ob ein User mit diesem Username bereits registriert ist und wenn ja, ob das Passwort übereinstimmt.

Bei Erfolg erhaltet wird bei ein **'response'** Event ausgelöst, welches ihr in eurem Client berücksichtigen solltet.
Ihr werdet bei diesem Event eine JSON erhalten, diese hat die Keys: 

**'status'**
- login_success, bei erfolgreichen Anmelden
- login_failed, bei fehlgeschlagenem Anmelden
  

**'message'** -
- Enthält mehr Informationen (Willkommensnachricht, Falscher User/Falsches Passwort)

### Register

Es wird das gleiche JSON wie beim Login benötigt und der Server löst auch hier ein **'response'** Event bei euch aus.

Als Antwort erhaltet ihr als Status entweder **'register_failed'** oder **'register_success'**, beide mit weiteren Informationen in der **'message'**.

