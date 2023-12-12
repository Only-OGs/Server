import json
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


# Gebe alle Clients in der Server Konsole aus
def get_clients():
    for client in connected_clients:
        print("*", client, "*")


# Kriege den Client Objekt zur passenden SID
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


# Lobby starten
def start_lobby(lobby):
    # TODO: Lobby starten
    return


def leave_lobby(sid):
    client = get_client(sid)
    old_lobby = client.current_lobby

    events.sio.leave_room(sid, old_lobby.id)
    old_lobby.remove_client(client)


    response_data = {'status': 'left', 'message': f"{old_lobby.get_players()}", 'lobby': old_lobby.id}

    print("sent ", response_data, " to ", sid)

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
    print("sent ", response_data, " to ", sid)


# Prüft, ob Client bereits eingeloggt ist
def is_already_on(name):
    for client in connected_clients:
        if client.username == name:
            return True
    return False


# Generiert eine Strecke für das Rennen der Lobby
def generate_track():
    print("generate new track...")
    # segments = random.randint(40, 60)
    segments = 3
    track = []

    for i in range(0, segments):
        temp_dict = {
            'segment_length': random.randint(50, 200),
            'curve_strength': random.randint(-6, 6),
            'hill_height': 0
        }
        track.append(temp_dict)

    return track
