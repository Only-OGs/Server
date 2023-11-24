import random
import string
import events

# Clients die aktuell connected sind, Value ist True, wenn diese nur connected sind,
# sind sie tatsächlich eingeloggt haben sie einen Username
connected_clients = {}

# User die aktuell registriert sind
users = {}

# Pfad zum
file_path = "users.txt"

# Set aus Lobbies
lobbies = set()


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


def get_lobby():
    lobby = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    lobbies.add(lobby)
    return lobby


def get_lobby_list(lobby):
    lobby_string = ""
    for client in connected_clients:
        if connected_clients[client]["lobby"] == lobby:
            if connected_clients[client]["name"] != False:
                lobby_string += connected_clients[client]["name"] + ";"
    return lobby_string[:-1]

def get_lobby_size(lobby):
    lobby_size = 0
    for client in connected_clients:
        if connected_clients[client]["lobby"] == lobby:
            print(connected_clients[client]["name"])
            lobby_size += 1
    return lobby_size
def start_lobby(lobby):
    # TODO: Lobby starten
    return

def leave_lobby(sid):
    old_lobby = connected_clients[sid]["lobby"]
    connected_clients[sid]["lobby"] = False
    events.sio.leave_room(sid, old_lobby)
    response_data = {'status': 'left', 'message': f"{get_lobby_list(old_lobby)}", 'lobby': old_lobby}
    events.sio.emit('player_leave', response_data, room=old_lobby)

def join_lobby(sid, new_lobby):
    connected_clients[sid]["lobby"] = new_lobby
    response_data = {'status': 'joined', 'message': f"{get_lobby_list(new_lobby)}", 'lobby': new_lobby}
    events.sio.enter_room(sid, new_lobby)
    events.sio.emit('player_joined', response_data, room=new_lobby)