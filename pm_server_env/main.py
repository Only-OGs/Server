import socketio
import eventlet

# Server erstellen
sio = socketio.Server(async_handlers=True,cors_allowed_origins='*')

# WSGI App
app = socketio.WSGIApp(sio)

# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    print(f"Client connected: {sid}")

# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    print(f"Client disconnected: {sid}")

# Event Handler für eingehende Nachrichten
@sio.event
def message(sid, data):
    try:
        # Hier gehen wir davon aus, dass der empfangene Datenstring ein JSON-Objekt ist
        json_data = sio.manager.rooms[sid].decode(data)

        # Beispielverarbeitung
        print(f"Received JSON from {sid}: {json_data}")

        # Antwort an Client
        response_data = {'status': 'success', 'message': 'JSON received successfully'}
        sio.emit('response', response_data, room=sid)

    except Exception as e:
        print(f"Error processing JSON from {sid}: {e}, {data}")

if __name__ == '__main__':
    # Starten mit eventlet
    eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)
