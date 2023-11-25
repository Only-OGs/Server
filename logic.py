import random
import string
import events

# Clients die aktuell connected sind, Value ist True, wenn diese nur connected sind,
# sind sie tatsächlich eingeloggt haben sie einen Username
connected_clients = list()

# User die aktuell registriert sind
users = {}

# Pfad zum
file_path = "users.txt"

# Set aus Lobbies
lobbies = set()


def get_clients():
    for client in connected_clients:
        print(client)


def get_client(sid):
    for client in connected_clients:
        if client.sid == sid:
            return client


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


def get_lobby_code():
    lobby = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    lobbies.add(lobby)
    return lobby


def get_lobby_list(lobby):
    lobby_string = ""
    for client in connected_clients:
        if connected_clients[client]["lobby"] == lobby:
            if connected_clients[client]["name"] is not False:
                lobby_string += connected_clients[client]["name"] + ";"
    return lobby_string[:-1]


def get_lobby_size(lobby):
    lobby_size = 0
    for client in connected_clients:
        if connected_clients[client]["lobby"] == lobby:
            lobby_size += 1
    return lobby_size


def start_lobby(lobby):
    # TODO: Lobby starten
    return


def get_lobbies():
    lobby_string = ""

    for lobby in lobbies:
        lobby_string += lobby + ", "

    return lobby_string[:-2]


def leave_lobby(sid):
    client = get_client(sid)
    old_lobby = connected_clients[client].current_lobby
    old_lobby.remove_client(client)
    events.sio.leave_room(sid, old_lobby.id)
    response_data = {'status': 'left', 'message': f"{old_lobby.get_players}", 'lobby': old_lobby.id}
    print("sent ", response_data, " to ", sid)
    events.sio.emit('player_leave', response_data, room=old_lobby)

    if get_lobby_size(old_lobby) == 0:
        print(old_lobby.id, " deleted, lobbies available: ", get_lobbies())
        lobbies.remove(old_lobby)


def get_lobby(code):
    for lobby in lobbies:
        if lobby.id == code:
            return lobby

def join_lobby(sid, new_lobby):
    client = get_client(sid)
    lobby = get_lobby(new_lobby)
    lobby.add_client(client)
    response_data = {'status': 'joined', 'message': f"{lobby.get_players()}", 'lobby': new_lobby}
    events.sio.enter_room(sid, new_lobby)
    events.sio.emit('player_joined', response_data, room=new_lobby)
    print("sent ", response_data, " to ", sid)


def is_already_on(name):
    for client in connected_clients:
        if client.username == name:
            return True

    return False
