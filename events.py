import socketio
import logic
import eventlet
from Entities import Client as Client
from Entities import Lobby as Lobby

sio = socketio.Server(async_handlers=True, cors_allowed_origins='*')
app = socketio.WSGIApp(sio)


# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    client = Client.Client(sid)
    logic.connected_clients.append(client)
    sio.emit('connection_success', sid, room=sid)
    print(f"Client connected: {sid}, Current Players: {logic.get_clients()}")


# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    client = logic.get_client(sid)
    lobby = client.current_lobby

    if lobby is not False:
        logic.leave_lobby(sid)
    logic.connected_clients.remove(client)

    print(f"Client disconnected: {sid}, Current Players: {logic.get_clients()}")


@sio.event
def leave_lobby(sid):
    logic.leave_lobby(sid)


@sio.event
def start_game(sid):
    client = logic.get_client(sid)
    lobby = logic.get_lobby_by_code(client.current_lobby.id)

    print(f"received go request from {client.username}")
    if not lobby.gameStarted:
        track = logic.generate_track()
        lobby.gameStarted = True

        sio.emit("game_start", "go", room=lobby.id)
        sio.emit("receive_track", track, room=lobby.id)

        print(f"sent go to lobby: {lobby.id}")
        print(f"sent following track -> \n {track} \n to {client.username}")

        return

    print(f"did nothing because game has already started @ {client.username}")


# Login, prüft Benutzernamen auf Existenz und in solchem Fall auch auf korrektes Passwort
@sio.event
def login(sid, data):
    print("received ", data, " from ", sid)
    client = logic.get_client(sid)

    name = data["user"]
    password = data["password"]

    if logic.is_already_on(name):
        response_data = {
            'status': 'login_failed',
            'message': "Benutzer bereits angemeldet"}
        sio.emit('login', response_data, room=sid)
        return

    if name in logic.users:
        if logic.users[name] == password:
            client.username = name
            response_data = {
                'status': 'login_success',
                'message': f"Login erfolgreich, willkommen {name}"
            }
        else:
            response_data = {
                'status': 'login_failed',
                'message': "Kombination aus Username und Passwort nicht korrekt"
            }
    else:
        response_data = {
            'status': 'login_failed',
            'message': f"Kombination aus Username und Passwort nicht korrekt"}

    sio.emit('login', response_data, room=sid)

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
        if client.current_lobby is not False:
            logic.leave_lobby(sid)
        print(str(name) + " wurde ausgeloggt.")
    except Exception as e:
        response_data = {'status': 'logout_failed', 'message': "Fehler beim Logout"}

    sio.emit('logout', response_data, room=sid)

    print("sent ", response_data, " to ", sid)


# Registrierung, prüft ob User bereits existiert, sollte dem nicht so sein, wird er, angelegt
@sio.event
def register(sid, data):
    print("received ", data, " from ", sid)
    name = data["user"]

    if name in logic.users:
        response_data = {'status': 'register_failed', 'message': f"{name} ist bereits registriert"}
    else:
        logic.write_user_to_file(data, sid)
        response_data = {'status': 'register_success', 'message': f"{name} wurde erfolgreich registriert"}

    sio.emit('register', response_data, room=sid)

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

    sio.emit('new_message', name + ";" + chat_message, room=lobby.id)
    print("LOBBY -", lobby.id, ": ", name, " sent message -> ", chat_message)


@sio.event
def is_ready(sid):
    print(sid, " wants to be ready")
    client = logic.get_client(sid)
    lobby = client.current_lobby
    lobby.is_ready(client)

    response_data = {
        'status': 'joined',
        'message': f"{client.username} ist Lobby {lobby.id} beigetreten",
        'lobby': lobby.id,
        'players': lobby.get_players(),
        'ready': lobby.get_ready_string()
    }

    sio.emit('lobby_management', response_data, room=lobby.id)


@sio.event
def not_ready(sid):
    print(sid, " wants to be not ready anymore")
    client = logic.get_client(sid)
    lobby = client.current_lobby
    lobby.not_ready(client)

    response_data = {
        'status': 'joined',
        'message': f"{client.username} ist Lobby {lobby.id} beigetreten",
        'lobby': lobby.id,
        'players': lobby.get_players(),
        'ready': lobby.get_ready_string()
    }

    sio.emit('lobby_management', response_data, room=lobby.id)


@sio.event
def join_lobby(sid, data):
    print("received ", data, " from ", sid)
    response_data = "nothing"
    new_lobby = logic.get_lobby_by_code(data["lobby"])

    if new_lobby in logic.lobbies:
        if logic.get_lobby_size(new_lobby) < 8:
            logic.join_lobby(sid, new_lobby)
            response_data = {
                'status': 'success',
                'message': f"Lobby beigetreten",
                'lobby': new_lobby.id,
                'players': ''}
        else:
            response_data = {
                'status': 'failed',
                'message': f"Lobby ist bereits voll",
                'lobby': new_lobby.id,
                'players': ''}
    else:
        response_data = {
            'status': 'failed',
            'message': f"Lobby existiert nicht",
            'lobby': data["lobby"],
            'players': ''}

    sio.emit("search_lobby", response_data, room=sid)

    print(logic.connected_clients)
    print(logic.users)
    print("sent ", response_data, " to ", sid)


@sio.event
def client_is_ingame(sid):
    print(sid, " is ingame")
    client = logic.get_client(sid)
    lobby = client.current_lobby
    lobby.place_client_on_position(client)

@sio.event
def ingame_pos(sid, data):
    pos = data["pos"]
    offset = data["offset"]
    client = logic.get_client(sid)
    id = client.username
    lobby = client.current_lobby
    lobby.update_pos(client, pos, offset)

@sio.event
def get_lobby(sid):
    print("received random lobby request from ", sid)

    response_data = {
        'status': 'failed',
        'message': 'Keine Lobby gefunden'
    }

    for lobby in logic.lobbies:
        if logic.get_lobby_size(lobby) < 8 and not lobby.gameStarted:
            logic.join_lobby(sid, lobby)
            response_data = {
                'status': 'success',
                'message': 'Lobby gefunden'
            }
            sio.emit("get_lobby", response_data, room=sid)
            return

    sio.emit("get_lobby", response_data, room=sid)
