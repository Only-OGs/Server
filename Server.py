import socketio
import eventlet
import json
import Logic

# Server erstellen
sio = socketio.Server(async_handlers=True, cors_allowed_origins='*')

# WSGI App
app = socketio.WSGIApp(sio)




# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    Logic.connected_clients[sid] = True
    sio.emit('connection_success', sid, room=sid)
    print(f"Client connected: {sid}, Current Players: {Logic.connected_clients}")


# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    Logic.connected_clients.pop(sid)
    print(f"Client disconnected: {sid}, Current Players: {Logic.connected_clients}")


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

    if name in Logic.users:
        if Logic.users[name] == password:
            Logic.connected_clients[sid] = name
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

    if name in Logic.users:
        response_data = {'status': 'register_failed', 'message': f"{name} ist bereits registriert"}
    else:
        Logic.write_user_to_file(data, sid)
        response_data = {'status': 'register_success', 'message': f"{name} wurde erfolgreich registriert"}

    sio.emit('response', response_data, room=sid)