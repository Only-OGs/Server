import random
import string
import threading

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
    lobbyString = ""
    for client in connected_clients:
        if connected_clients[client]["lobby"] is lobby:
            lobbyString += connected_clients[client]["name"] + ";"
    return lobbyString[:-1]

def start_lobby(lobby):
    #TODO: Lobby starten
    return