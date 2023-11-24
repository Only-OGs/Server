import logic
import events


if __name__ == '__main__':
    # User laden
    logic.load_registered_users()
    # Starten mit eventlet
    events.eventlet.wsgi.server(events.eventlet.listen(('0.0.0.0', 8080)), events.app)
