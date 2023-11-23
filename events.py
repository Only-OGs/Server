import socketio
import eventlet
import json
import logic

sio = socketio.Server(async_handlers=True, cors_allowed_origins='*')
app = socketio.WSGIApp(sio)


# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    logic.connected_clients[sid] = {"username": False, "lobby": False}
    sio.emit('connection_success', sid, room=sid)
    print(f"Client connected: {sid}, Current Players: {logic.connected_clients}")


# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    logic.connected_clients.pop(sid)
    print(f"Client disconnected: {sid}, Current Players: {logic.connected_clients}")


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

    if name in logic.users:
        if logic.users[name] == password:
            logic.connected_clients[sid]["name"] = name
            response_data = {'status': 'login_success', 'message': f"Login erfolgreich, willkommen {name}"}
        else:
            response_data = {'status': 'login_failed', 'message': "Passwort nicht korrekt"}
    else:
        response_data = {'status': 'login_failed', 'message': f"{name} ist nicht registriert."}

    sio.emit('response', response_data, room=sid)

    print("sent ", response_data, " to ", sid)


@sio.event
def logout(sid, data):
    try:
        name = logic.connected_clients[sid]
        response_data = {'status': 'logout_success',
                         'message': f"{logic.connected_clients[sid]} erfolgreich ausgeloggt"}
        logic.connected_clients[sid][name] = False
        print(name + " wurde ausgeloggt.")
    except Exception as e:
        response_data = {'status': 'logout_failed', 'message': "Fehler beim Logout"}

    sio.emit('response', response_data, room=sid)

    print("sent ", response_data, " to ", sid)

# Registrierung, prüft ob User bereits existiert, sollte dem nicht so sein wird er angelegt
@sio.event
def register(sid, data):
    name = data["user"]
    password = data["password"]

    if name in logic.users:
        response_data = {'status': 'register_failed', 'message': f"{name} ist bereits registriert"}
    else:
        logic.write_user_to_file(data, sid)
        response_data = {'status': 'register_success', 'message': f"{name} wurde erfolgreich registriert"}

    sio.emit('response', response_data, room=sid)

    print("sent ", response_data, " to ", sid)

# Client will Lobby erstellen
@sio.event
def create_lobby(sid):
    lobby = logic.get_lobby()
    logic.connected_clients[sid]["lobby"] = lobby
    sio.enter_room(sid, lobby)
    response_data = {'status': 'lobby_created', 'message': f"{lobby}"}
    sio.emit('response', response_data)

    print("sent ", response_data, " to ", sid)

@sio.event
def join_lobby(sid, data):
    new_lobby = data["lobby"]
    if new_lobby in logic.lobbies:
        logic.connected_clients[sid]["lobby"] = new_lobby
        response_data = {'status': 'joined', 'message': f"{logic.get_lobby_list(new_lobby)}"}
        sio.emit('player_joined', response_data, room=data["lobby"])
        sio.enter_room(sid, new_lobby)
    else:
        response_data = {'status': 'failed', 'message': f"Fehler beim Beitritt von {new_lobby}"}
    sio.emit('player_joined', response_data, room=sid)

    print("sent ", response_data, " to ", sid)

