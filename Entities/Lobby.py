import logic
import threading
import time
import events


class Lobby:
    def __init__(self):
        self.id = logic.generate_lobby_code()
        self.clients = set()
        self.gameStarted = False
        self.allReady = False
        self.connections = 0
        self.isReady = set()

        logic.lobbies.add(self)

    def __str__(self):
        return f"LobbyID: {self.id}, Users in Lobby: {self.clients}, Game has started: {self.gameStarted}"

    def add_client(self, client):
        client.current_lobby = self
        self.clients.add(client)
        self.connections += 1

    def remove_client(self, client):
        client.current_lobby = False

        self.clients.remove(client)

        self.connections -= 1

        # Zerstöre Lobby wenn leer
        if self.connections == 0:
            print(self.id, ' deleted')
            logic.lobbies.remove(self)

        return True

    # Gebe String mit Namen der Spieler getrennt durch ; wieder
    def get_players(self):
        player_string = ""

        for client in self.clients:
            player_string += client.username + ";"

        return player_string[:-1]

    def is_ready(self, client):
        self.isReady.add(client)
        print(client.username, " in lobby ", self.id, " is ready")
        self.check_all_ready()

    def not_ready(self, client):
        self.isReady.remove(client)
        print(client.username, " in lobby ", self.id, " is not ready")
        self.check_all_ready()

    # Sind gleich viele Clients verbunden wie Ready beginnt der Timer zum Spielstart
    def check_all_ready(self):
        print("Aufruf check all ready")
        if len(self.clients) == len(self.isReady):
            self.allReady = True

        if self.allReady and len(self.clients) > 1:
            print("Rufe init game start auf")
            self.init_game_start()

        return self.allReady

    # Timer, der Spiel startet und Restzeit an Clients übermittelt, bricht ab sollte jemand nicht mehr Ready sein
    def _timer(self):
        counter = 10

        print("Start counting the timer")
        time.sleep(1)

        while counter != 0:

            if not self.check_all_ready():
                events.sio.emit("timer_abrupt", "ITS OVER", room=self.id)

            print(self.id, " counter is ", counter)
            time.sleep(100)
            counter -= 1
            events.sio.emit("timer_countdown", "", room=self.id)

        events.sio.emit("START_THE_FUCKING_GAME", "DO IT NOW", room=self.id)

    # Startet einen Thread in der die Timer Methode ausgeführt wird
    def init_game_start(self):
        print("Initiate thread for timer")
        time.sleep(1)
        if not self.gameStarted:
            self.gameStarted = True
            threading.Thread(target=self._timer, daemon=False).start()
