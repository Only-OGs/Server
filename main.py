import socketio
import eventlet

# Create a Socket.IO server
sio = socketio.Server(cors_allowed_origins='*')

# Create a WSGI app for the server
app = socketio.WSGIApp(sio)

# Define an event handler for the 'message' event
@sio.event
def message(sid, data):
    print(f"Received message: {data}")
    # Send a response to the client
    sio.emit('response', f"Server received your message: {data}", room=sid)

if __name__ == '__main__':
    # Start the server using eventlet
    eventlet.wsgi.server(eventlet.listen(('localhost', 8080)), app)
