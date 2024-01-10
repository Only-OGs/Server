import events


if __name__ == '__main__':
    # Starten mit eventlet
    events.eventlet.wsgi.server(events.eventlet.listen(('0.0.0.0', 8080)), events.app)
