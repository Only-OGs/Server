import events
import logging as log

if __name__ == '__main__':
    log.basicConfig()
    log.root.setLevel(log.NOTSET)
    log.basicConfig(level=log.NOTSET)

    handle = "OGRacerServer"
    logging = log.getLogger(handle)

    # Starten mit eventlet
    events.eventlet.wsgi.server(events.eventlet.listen(('0.0.0.0', 8080)), events.app)
