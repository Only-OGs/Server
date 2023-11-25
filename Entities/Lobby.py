import logic


class Lobby:
    def __init__(self):
        self.id = logic.get_lobby_code()
        self.clients = set()
        self.gameStarted = False
        self.connections = 0

        logic.lobbies.add(self.id)

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
        if self.connections == 0:
            print(self.id, ' deleted')
            logic.lobbies.remove(self)

        return True

    def get_players(self):
        player_string = ""

        for client in self.clients:
            player_string += client.name + ";"

        return player_string[:-1]
