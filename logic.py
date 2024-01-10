import random
import string
import events
import logging as log
handle = "my-app"
logging = log.getLogger(handle)

# Clients die aktuell connected sind, Value ist True, wenn diese nur connected sind,
# sind sie tatsächlich eingeloggt haben sie einen Username
connected_clients = list()

# User die aktuell registriert sind
users = {}

# Set aus Lobbies
lobbies = set()


# Gebe alle Clients in der Server Konsole aus
def get_clients():
    for client in connected_clients:
        logging.info(f"* {client} *")


# Kriege den Client Objekt zur passenden SID
def get_client(sid):
    for client in connected_clients:
        if client.sid == sid:
            return client


# Generiere Lobby Code
def generate_lobby_code():
    lobby = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    return lobby


# Kriege Anzahl der Spieler in Lobby
def get_lobby_size(lobby):
    lobby_size = 0

    for client in connected_clients:
        if client.current_lobby == lobby:
            lobby_size += 1

    return lobby_size


# Kriege Lobby Objekt durch Code
def get_lobby_by_code(code):
    for lobby in lobbies:
        if lobby.id == code:
            return lobby


# Entferne Client aus Lobby
def leave_lobby(sid):
    client = get_client(sid)
    old_lobby = client.current_lobby

    events.sio.leave_room(sid, old_lobby.id)

    old_lobby.remove_client(client)

    response_data = {'status': 'left', 'message': f"{old_lobby.get_players()}", 'lobby': old_lobby.id}

    logging.info(f"sent {response_data} to {sid}")

    events.sio.emit('player_leave', response_data, room=old_lobby.id)


# Spieler einer Lobby hinzufügen, Hilfsmethode für einige Events
def join_lobby(sid, new_lobby):
    client = get_client(sid)
    lobby = new_lobby
    lobby.add_client(client)

    response_data = {
        'status': 'joined',
        'message': f"{client.username} ist Lobby {lobby.id} beigetreten",
        'lobby': lobby.id,
        'players': lobby.get_players(),
        'ready': lobby.get_ready_string()
    }

    events.sio.enter_room(sid, new_lobby.id)
    events.sio.emit('lobby_management', response_data, room=new_lobby.id)
    logging.info(f"sent  {response_data} to {sid}")


# Prüft, ob Client bereits eingeloggt ist
def is_already_on(name):
    for client in connected_clients:
        if client.username == name:
            return True
    return False


# Generiert Assets für die Strecke
def generate_track_assets(track_length):
    amounts = track_length // 5000
    assets = []

    for i in range(amounts):
        asset = {
            'model': random.randint(0, 23),
            'pos': i * 5000,
            'side': random.choice([1.5, -1.5])
        }
        assets.append(asset)
    return assets
