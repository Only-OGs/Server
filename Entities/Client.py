#
#   Diese Klasse bündelt alle Informationen der Clients in Objekte
#

class Client:
    def __init__(self, sid):
        self.sid = sid
        self.username = False
        self.current_lobby = False
        self.pos = dict()

    def __str__(self):
        return f"SID: {self.sid}, Username: {self.username}, Current Lobby: {self.current_lobby}"

    def set_lobby(self, lobby):
        self.current_lobby = lobby
