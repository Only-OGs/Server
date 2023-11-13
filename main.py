import socketio
import eventlet
import json

# Server erstellen
sio = socketio.Server(async_handlers=True, cors_allowed_origins='*')

# WSGI App
app = socketio.WSGIApp(sio)

connected_clients = {}


# Verbindung eines neuen Clients
@sio.event
def connect(sid, environ):
    connected_clients[sid] = True
    sio.emit('connection_success', sid, room=sid)
    print(f"Client connected: {sid}, Current Players: {connected_clients}")


# Verbindungsabbruch eines Clients
@sio.event
def disconnect(sid):
    connected_clients.pop(sid)
    print(f"Client disconnected: {sid}, Current Players: {connected_clients}")


# Event Handler für eingehende Nachrichten
@sio.event
def message(sid, data):
    try:
        # Beispielverarbeitung
        print(f"Received JSON from {sid}: {data}")

        # Antwort an Client
        response_data = {'status': 'success', 'message': 'JSON received successfully'}
        sio.emit('response', response_data, room=sid)

    except Exception as e:
        print(f"Error processing JSON from {sid}: {e}, {data}")


if __name__ == '__main__':
    # Starten mit eventlet
    eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)
