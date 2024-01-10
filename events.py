import socketio
import logic
import eventlet
from Entities import Client as Client
from Entities import Lobby as Lobby
from sqlite.database import Database
import logging as log
handle = "my-app"
logging = log.getLogger(handle)

sio = socketio.Server(async_handlers=True, cors_allowed_origins='*')
app = socketio.WSGIApp(sio)
db = Database("og_racer.db")


# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    client = Client.Client(sid)
    logic.connected_clients.append(client)
    sio.emit('connection_success', sid, room=sid)
    logging.info(f"Client connected: {sid}, Current Players: {logic.get_clients()}")


# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    client = logic.get_client(sid)
    lobby = client.current_lobby

    if lobby is not False:
        logic.leave_lobby(sid)
    logic.connected_clients.remove(client)

    logging.info(f"Client disconnected: {sid}, Current Players: {logic.get_clients()}")


# Client will Lobby verlassen
@sio.event
def leave_lobby(sid):
    logic.leave_lobby(sid)


# Login, prüft Benutzernamen auf Existenz und in solchem Fall auch auf korrektes Passwort
@sio.event
def login(sid, data):
    logging.info(f"received {data} from {sid}")
    client = logic.get_client(sid)

    name = data["user"]
    password = data["password"]

    if logic.is_already_on(name):
        response_data = {
            'status': 'login_failed',
            'message': "Benutzer bereits angemeldet"}
        sio.emit('login', response_data, room=sid)
        return

    if db.user_exist(name):
        if db.check_credentials(name, password):
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

    logging.info(f"sent {response_data} to {sid}")


# Client loggt sich aus
@sio.event
def logout(sid):
    logging.info(f"received logout request from {sid}")
    client = logic.get_client(sid)

    try:
        name = client.username

        response_data = {'status': 'logout_success',
                         'message': f"{name} erfolgreich ausgeloggt"}
        client.username = False
        if client.current_lobby is not False:
            logic.leave_lobby(sid)
        logging.info(f"{str(name)} wurde ausgeloggt.")
    except Exception as e:
        response_data = {'status': 'logout_failed', 'message': "Fehler beim Logout"}

    sio.emit('logout', response_data, room=sid)

    logging.info(f"sent  {response_data} to {sid}")


# Registrierung, prüft ob User bereits existiert, sollte dem nicht so sein, wird er, angelegt
@sio.event
def register(sid, data):
    logging.info(f"received  {data}  from  {sid}")
    name = data["user"]
    password = data["password"]

    if db.user_exist(name):
        response_data = {'status': 'register_failed', 'message': f"{name} ist bereits registriert"}
    else:
        db.add_user(name, password)
        response_data = {'status': 'register_success', 'message': f"{name} wurde erfolgreich registriert"}

    sio.emit('register', response_data, room=sid)

    logging.info(f"sent  {response_data} to {sid}")


# Client will Lobby erstellen
@sio.event
def create_lobby(sid):
    logging.info(f"received lobby request from {sid}")
    client = logic.get_client(sid)

    lobby = Lobby.Lobby()
    lobby.add_client(client)

    sio.enter_room(sid, lobby.id)

    response_data = {'status': 'lobby_created', 'message': f"{lobby.id}"}

    sio.emit('lobby_created', response_data, room=sid)

    logging.info(f"sent  {response_data} to {sid}")


# Chat-Nachrichten in Lobby
@sio.event
def sent_message(sid, chat_message):
    client = logic.get_client(sid)

    name = client.username
    lobby = client.current_lobby

    sio.emit('new_message', name + ";" + chat_message, room=lobby.id)
    logging.info(f"LOBBY - {lobby.id} : {name}  sent message ->  {chat_message}")


# Client erklärt sich bereit
@sio.event
def is_ready(sid):
    logging.info(f"{sid} wants to be ready")
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


# Client erklärt sich nicht mehr bereit
@sio.event
def not_ready(sid):
    logging.info(f"{sid} wants to be not ready anymore")
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


# Client will Lobby per Code beitreten
@sio.event
def join_lobby(sid, data):
    logging.info("received ", data, " from ", sid)
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

    logging.info(logic.connected_clients)
    logging.info(logic.users)
    logging.info(f"sent {response_data} to  {sid}")


# Client gibt an das er das Spiel geladen hat
@sio.event
def client_is_ingame(sid):
    logging.info(f"{sid} is ingame")
    client = logic.get_client(sid)
    lobby = client.current_lobby
    lobby.place_client_on_position(client)


# Client gibt aktuelle Ingame Position durch
@sio.event
def ingame_pos(sid, data):
    pos = data["pos"]
    offset = data["offset"]
    client = logic.get_client(sid)
    id = client.username
    lobby = client.current_lobby
    lobby.update_pos(client, pos, offset)


# Client will zufällige Lobby haben
@sio.event
def get_lobby(sid):
    logging.info(f"received random lobby request from {sid}")

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


# Client benötigt Watcher für die Rundenzeit
@sio.event
def start_watch(sid):
    client = logic.get_client(sid)
    lobby = client.current_lobby

    lobby.start_watcher(client.username)


# Client möchte das Spiel verlassen
@sio.event
def game_leave(sid):
    client = logic.get_client(sid)
    lobby = client.current_lobby

    lobby.player_leave(client.username)
