import socketio
import eventlet

# Server erstellen
sio = socketio.Server(cors_allowed_origins='*')

# WSGI App
app = socketio.WSGIApp(sio)

# Event Handler für eingehende Nachrichten
@sio.event
def message(sid, data):
    print(f"Received message: {data}")
    # Sende Antwort an Client
    sio.emit('response', f"Server received your message: {data}", room=sid)

if __name__ == '__main__':
    # Starten mit eventlet
    eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)
