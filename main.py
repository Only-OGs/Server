import socketio
import eventlet
import json

# Server erstellen
sio = socketio.Server(async_handlers=True, cors_allowed_origins='*')

# WSGI App
app = socketio.WSGIApp(sio)

# Clients die aktuell connected sind, Value ist True, wenn diese nur connected sind,
# sind sie tatsächlich eingeloggt haben sie einen Username
connected_clients = {}

# User die aktuell registriert sind
users = {}

# Pfad zum
file_path = "users.txt"


# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    connected_clients[sid] = True
    sio.emit('connection_success', sid, room=sid)
    print(f"Client connected: {sid}, Current Players: {connected_clients}")


# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    connected_clients.pop(sid)
    print(f"Client disconnected: {sid}, Current Players: {connected_clients}")


# Event Handler für eingehende Nachrichten
@sio.event
def message(sid, data):
    try:
        print(f"Received JSON from {sid}: {data}")
        json_data = json.load(data)

        # Antwort an Client
        response_data = {'status': 'success', 'message': 'JSON received successfully'}
        sio.emit('response', response_data, room=sid)
    except Exception as e:
        print(f"Error processing JSON from {sid}: {e}, {data}")


# Login, prüft Benutzernamen auf Existenz und in solchem Fall auch auf korrektes Passwort
@sio.event
def login(sid, data):
    name = data["user"]
    password = data["password"]

    if name in users:
        if users[name] == password:
            connected_clients[sid] = name
            response_data = {'status': 'login_success', 'message': f"Login erfolgreich, willkommen {name}"}
        else:
            response_data = {'status': 'login_failed', 'message': "Passwort nicht korrekt"}
    else:
        response_data = {'status': 'login_failed', 'message': f"{name} ist nicht registriert."}

    sio.emit('response', response_data, room=sid)


# Registrierung, prüft ob User bereits existiert, sollte dem nicht so sein wird er angelegt
@sio.event
def register(sid, data):
    name = data["user"]
    password = data["password"]

    if name in users:
        response_data = {'status': 'register_failed', 'message': f"{name} ist bereits registriert"}
    else:
        write_user_to_file(data, sid)
        response_data = {'status': 'register_success', 'message': f"{name} wurde erfolgreich registriert"}

    sio.emit('response', response_data, room=sid)


# User die registriert werden, werden in die users.txt geschrieben und anschließend zur
# Laufzeit in das User dict aufgenommen
def write_user_to_file(data, sid):
    name = data["user"]
    password = data["password"]

    try:
        with open(file_path, 'a') as file:
            file.write(f"{name} {password}\n")

        print(f"Die Benutzerdaten wurden erfolgreich in die Datei {file_path} geschrieben.")
        users[name] = password

    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")


# Lädt registrierte User aus users.txt in das User dict
def load_registered_users():
    try:
        with open(file_path, 'r') as file:
            for line in file:
                # Annahme: Benutzername und Passwort sind durch ein Leerzeichen getrennt
                username, password = line.strip().split()
                users[username] = password

    except FileNotFoundError:
        print(f"Die Datei {file_path} wurde nicht gefunden.")
        return None
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten: {e}")
        return None


if __name__ == '__main__':
    # User laden
    load_registered_users()
    # Starten mit eventlet
    eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)
