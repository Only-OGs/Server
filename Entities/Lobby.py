import eventlet

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
        self.timer_started = False

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

        if client in self.isReady:
            self.isReady.remove(client)

        self.connections -= 1

        # Zerstöre Lobby wenn leer
        if self.connections == 0:
            print(self.id, ' deleted')
            logic.lobbies.remove(self)

        if self.check_all_ready():
            self.init_game_start()

        response_data = {
            'status': 'joined',
            'message': f"{client.username} hat Lobby {self.id} verlassen.",
            'lobby': self.id,
            'players': self.get_players()}

        events.sio.emit('lobby_management', response_data, room=self.id)

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

        if (self.allReady and len(self.clients) > 1) and not self.timer_started:
            self.init_game_start()

    def not_ready(self, client):
        self.isReady.remove(client)
        print(client.username, " in lobby ", self.id, " is not ready")
        self.check_all_ready()

        if (self.allReady and len(self.clients) > 1) and not self.timer_started:
            self.init_game_start()

    # Sind gleich viele Clients verbunden wie Ready beginnt der Timer zum Spielstart
    def check_all_ready(self):
        self.allReady = False

        if len(self.clients) == len(self.isReady) and len(self.clients) > 1:
            self.allReady = True

        return self.allReady

    def _timer_delay_set(self):
        eventlet.sleep(3)
        self.timer_started = False

    # Timer, der Spiel startet und Restzeit an Clients übermittelt, bricht ab sollte jemand nicht mehr Ready sein
    def _timer(self):
        counter = 10

        print("Start counting the timer")
        self.timer_started = True

        while counter != -2:
            if (not self.check_all_ready() and self.connections > 1) or self.connections == 1:
                events.sio.emit("timer_abrupt", "Timer has been abrupt", room=self.id)
                print("timer_abrupt sent to ", self.id)
                self.timer_started = False
                return



            print(self.id, " counter is ", counter)
            eventlet.sleep(1)
            events.sio.emit("timer_countdown", counter, room=self.id)
            print("sent countdown ", counter, " to ", self.id)
            counter -= 1

        if self.timer_started:
            self.gameStarted = True
            events.sio.emit("load_level", logic.generate_track(), room=self.id)

    # Startet einen Thread in der die Timer Methode ausgeführt wird
    def init_game_start(self):
        if not self.timer_started:
            print("Initiate thread for timer")
            eventlet.spawn(self._timer)
