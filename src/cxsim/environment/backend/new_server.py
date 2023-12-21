from flask import Flask
from flask_socketio import SocketIO


class FlaskSocketIOServer:
    def __init__(
            self,
            host='localhost',
            port=8765
    ):
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app)
        self.host = host
        self.port = port

        # Event handlers
        @self.socketio.on('connect')
        def handle_connect():
            print('Client connected')

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Client disconnected')

        @self.socketio.on('message')
        def handle_message(message):
            # Process the message here
            response = "none"
            self.socketio.emit('response', response)

    def run(self):
        self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug = True)


if __name__ == "__main__":
    server = FlaskSocketIOServer()
    server.run()
