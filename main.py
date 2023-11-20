import Logic
import Server



if __name__ == '__main__':
    # User laden
    Logic.load_registered_users()
    # Starten mit eventlet
    Server.eventlet.wsgi.server(Server.eventlet.listen(('localhost', 8080)), Server.app)
