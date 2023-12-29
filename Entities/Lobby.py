import random

import eventlet

import logic
import threading
import time
import events
import random


class Lobby:
    def __init__(self):
        self.id = logic.generate_lobby_code()
        self.max_players = 0
        self.clients = set()
        self.gameStarted = False
        self.raceStarted = False
        self.RaceFinished = False
        self.allReady = False
        self.connections = 0
        self.isReady = set()
        self.isIngame = set()
        self.timer_started = False
        self.track = logic.generate_track()
        self.track_length = self._init_track_length()
        self.positions = [
            {"offset": -0.66, "pos": 0, "id": 'NPC1', "npc": True, 'speed': random.randint(100, 220)},
            {"offset": 0, "pos": 0, "id": 'NPC2', "npc": True, 'speed': random.randint(100, 220)},
            {"offset": 0.66, "pos": 0, "id": 'NPC3', "npc": True, 'speed': random.randint(100, 220)},
            {"offset": -0.66, "pos": 800, "id": 'NPC4', "npc": True, 'speed': random.randint(100, 220)},
            {"offset": 0, "pos": 800, "id": 'NPC5', "npc": True, 'speed': random.randint(100, 220)},
            {"offset": 0.66, "pos": 800, "id": 'NPC6', "npc": True, 'speed': random.randint(100, 220)},
            {"offset": -0.66, "pos": 1600, "id": 'NPC7', "npc": True, 'speed': random.randint(100, 220)},
            {"offset": 0, "pos": 1600, "id": 'NPC8', "npc": True, 'speed': random.randint(100, 220)}
        ]
        logic.lobbies.add(self)

    def __str__(self):
        return f"LobbyID: {self.id}, Users in Lobby: {self.get_players()}, Game has started: {self.gameStarted}"

    def _init_track_length(self):
        length = 0
        for segment in self.track:
            length += segment.get('segment_length') * 3

        return length * 200

    def get_ready_string(self):
        ready_string = ""

        for client in self.isReady:
            ready_string += client.username + ";"

        return ready_string[:-1]

    def add_client(self, client):
        client.current_lobby = self
        self.clients.add(client)
        self.connections += 1

        response_data = {
            'status': 'joined',
            'message': f"{client.username} hat Lobby {self.id} betreten.",
            'lobby': self.id,
            'players': self.get_players(),
            'ready': self.get_ready_string()}

        events.sio.emit('lobby_management', response_data, room=client.sid)
        print("sent -> ", response_data, " to ", client.username)

    def update_pos(self, client, pos, offset):
        for record in self.positions:
            if record["id"] == client.username:
                record["pos"] = pos
                record["offset"] = offset
                break

        events.sio.emit("updated_positions", self.positions, room=self.id)

    def remove_client(self, client):
        client.current_lobby = False
        self.clients.remove(client)

        if client in self.isReady:
            self.isReady.remove(client)

        self.connections -= 1

        for entry in self.positions:
            if entry["id"] == client.username:
                entry["id"] = None

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
            'players': self.get_players(),
            'ready': self.get_ready_string()}

        events.sio.emit('lobby_management', response_data, room=self.id)
        print("sent -> ", response_data, " to ", client.username)
        return True

    # Gebe String mit Namen der Spieler getrennt durch ; wieder
    def get_players(self):
        player_string = ""

        for client in self.clients:
            status = ""
            if client in self.isReady:
                status = "  -  READY"
            player_string += client.username + status + ";"

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
        counter = 1

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
            self.max_players = len(self.clients)
            events.sio.emit("load_level", self.track, room=self.id)

    # Startet einen Thread in der die Timer Methode ausgeführt wird
    def init_game_start(self):
        if not self.timer_started:
            print("Initiate thread for timer")
            eventlet.spawn(self._timer)

    def get_new_offset(self, other_car, current_car):
        if other_car.get("offset") > 0.5:
            direction = -1
        elif other_car.get("offset") < -0.5:
            direction = 1
        else:
            if current_car.get("offset") > current_car.get("offset"):
                direction = 1
            else:
                direction = -1
        return direction * (1 / 25 * (current_car.get("speed") - other_car.get("speed")) / 12000)

    def overlap(self, x1, w1, x2, w2, percent):
        if percent is None:
            percent = 1
        half = percent / 2
        min1 = x1 - (w1 * half)
        max1 = x1 + (w1 * half)
        min2 = x2 - (w2 * half)
        max2 = x2 + (w2 * half)
        return not ((max1 < min2) or (min1 > max2))

    def avoid_check(self, current_player):
        for player in self.positions:
            if player is not current_player:
                if (1000 > (player['pos'] - current_player['pos']) > 0) and self.overlap(x1=player.get("offset"),
                                                                                         w1=0.3,
                                                                                         x2=current_player.get(
                                                                                             "offset"),
                                                                                         w2=0.3, percent=1.2):
                    new_offset = self.get_new_offset(player, current_player)
                    self.ai_avoid(new_offset, current_player)

    def ai_avoid(self, new_offset, player):
        player['offset'] += 250 * new_offset

    def _ai_racer(self):
        print("AI RACING STARTS - THREADED")
        while not self.RaceFinished:
            eventlet.sleep(float(1 / 60))
            positions = self.positions
            for client in positions:
                if client.get("npc") is True:
                    client["pos"] = (client.get("pos") + client.get('speed')) % self.track_length
                    self.avoid_check(client)

            events.sio.emit("updated_positions", self.positions, room=self.id)

    def _race_timer(self):
        events.sio.emit("start_race_timer", "Rennen beginnt..", room=self.id)
        eventlet.sleep(1)
        events.sio.emit("start_race_timer", "5", room=self.id)
        print(self.id," race begins in 5")
        eventlet.sleep(1)
        events.sio.emit("start_race_timer", "4", room=self.id)
        print(self.id, " race begins in 4")
        eventlet.sleep(1)
        events.sio.emit("start_race_timer", "3", room=self.id)
        print(self.id, " race begins in 3")
        eventlet.sleep(1)
        events.sio.emit("start_race_timer", "2", room=self.id)
        print(self.id, " race begins in 2")
        eventlet.sleep(1)
        events.sio.emit("start_race_timer", "1", room=self.id)
        print(self.id, " race begins in 1")
        eventlet.sleep(1)
        eventlet.spawn(self._ai_racer())
    def start_race(self):
        print("Start Race, self.raceStart is ", self.raceStarted)
        events.sio.emit("start_race", "Race Starts", room=self.id)
        self.raceStarted = True
        print("self.raceStart now is ", self.raceStarted)
        eventlet.spawn(self._race_timer())
        return

    def place_client_on_position(self, client):
        for position in self.positions:
            if position['npc'] is True:
                position['id'] = client.username
                position['npc'] = False
                break

        self.isIngame.add(client)
        events.sio.emit("wait_for_start", self.positions, room=self.id)
        print("sent :", self.positions, " -> ", client.username, " and everyone in his lobby")
        if len(self.isIngame) == self.max_players and not self.raceStarted:
            self.start_race()
