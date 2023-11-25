import socketio
import eventlet
import json
import logic
from Entities import Client as Client
from Entities import Lobby as Lobby

sio = socketio.Server(async_handlers=True, cors_allowed_origins='*')
app = socketio.WSGIApp(sio)


# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    client = Client.Client(sid)
    logic.connected_clients.add(client)
    sio.emit('connection_success', sid, room=sid)
    print(f"Client connected: {sid}, Current Players: {logic.get_clients()}")


# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    client = logic.get_client(sid)
    lobby = logic.get_lobby(client.current_lobby)

    lobby.remove_client(client)
    logic.connected_clients.remove(client)

    print(f"Client disconnected: {sid}, Current Players: {logic.get_clients()}")


@sio.event
def leave_lobby(sid):
    client = logic.get_client(sid)
    lobby = logic.get_lobby(client.current_lobby)

    if lobby.remove_client(client):
        sio.leave_room(sid, lobby.id)
        response_data = {'status': 'left', 'message': f"{lobby.get_players}", 'lobby': lobby.id}
        print("sent ", response_data, " to ", sid)
        sio.emit('player_leave', response_data, room=lobby.id)


# Login, prüft Benutzernamen auf Existenz und in solchem Fall auch auf korrektes Passwort
@sio.event
def login(sid, data):
    print("received ", data, " from ", sid)
    client = logic.get_client(sid)

    name = data["user"]
    password = data["password"]

    if logic.is_already_on(name):
        response_data = {'status': 'login_failed', 'message': "Benutzer bereits angemeldet"}
        sio.emit('response', response_data, room=sid)
        return

    if name in logic.users:
        if logic.users[name] == password:
            logic.connected_clients[client].username = name
            response_data = {'status': 'login_success', 'message': f"Login erfolgreich, willkommen {name}"}
        else:
            response_data = {'status': 'login_failed', 'message': "Passwort nicht korrekt"}
    else:
        response_data = {'status': 'login_failed', 'message': f"{name} ist nicht registriert."}

    sio.emit('response', response_data, room=sid)

    print("sent ", response_data, " to ", sid)


@sio.event
def logout(sid):
    print("received logout request from ", sid)
    client = logic.get_client(sid)

    try:
        name = client.username

        response_data = {'status': 'logout_success',
                         'message': f"{name} erfolgreich ausgeloggt"}
        client.username = False
        logic.leave_lobby(sid)
        print(str(name) + " wurde ausgeloggt.")
    except Exception as e:
        response_data = {'status': 'logout_failed', 'message': "Fehler beim Logout"}

    sio.emit('response', response_data, room=sid)

    print("sent ", response_data, " to ", sid)


# Registrierung, prüft ob User bereits existiert, sollte dem nicht so sein wird er angelegt
@sio.event
def register(sid, data):
    print("received ", data, " from ", sid)
    name = data["user"]

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
    print("received lobby request from ", sid)
    client = logic.get_client(sid)

    lobby = Lobby.Lobby()
    lobby.add_client(client)

    sio.enter_room(sid, lobby.id)

    response_data = {'status': 'lobby_created', 'message': f"{lobby.id}"}

    sio.emit('lobby_created', response_data, room=sid)

    print("sent ", response_data, " to ", sid)


@sio.event
def sent_message(sid, chat_message):
    client = logic.get_client(sid)

    name = client.username
    lobby = client.current_lobby

    sio.emit('new_message', name + ";" + chat_message, room=lobby)
    print("LOBBY -", lobby, ": ", name, " sent message -> ", chat_message)


@sio.event
def join_lobby(sid, data):
    print("received ", data, " from ", sid)
    response_data = "nothing"
    new_lobby = data["lobby"]

    if new_lobby in logic.lobbies:
        if logic.get_lobby_size(new_lobby) < 8:
            logic.join_lobby(sid, new_lobby)
        else:
            response_data = {'status': 'failed', 'message': f"Lobby ist bereits voll", 'lobby': new_lobby}
            sio.emit("player_joined", response_data, room=sid)
    else:
        response_data = {'status': 'failed', 'message': f"Lobby ist nicht bekannt", 'lobby': new_lobby}
        sio.emit("player_joined", response_data, room=sid)
    print(logic.connected_clients)
    print(logic.users)
    print("sent ", response_data, " to ", sid)


@sio.event
def get_lobby(sid):
    print("received random lobby request from ", sid)
    for lobby in logic.lobbies:
        if logic.get_lobby_size(lobby) < 8:
            logic.join_lobby(sid, lobby)
            sio.emit("get_lobby", "true", room=sid)
            return

    sio.emit("get_lobby", "false", room=sid)
