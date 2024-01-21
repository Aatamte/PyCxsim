import socketio
from typing import Dict
from cxsim.environment.client.environment_manager import EnvironmentConnection
import json


class SocketIOClient:
    def __init__(self, environment, host='localhost', port=8765):
        self.sio = socketio.Client(logger=True, engineio_logger=True, reconnection=False)
        self.url = f"http://{host}:{port}"
        self.environment = environment

        self.environment_connection = EnvironmentConnection(environment)

        self.connected = False  # Add a flag to track connection status
        self.has_registered = False

        # secure connection to the server
        self.phase_one: bool = False

        # pass environment metadata to the server
        self.phase_two: bool = False

        self.phase_three: bool = False

    def _phase_one(self):
        self.send_message('register_client', {'type': 'environment'})
        print("send message")

    def on_connect(self):
        self.connected = True  # Set flag to True when connected
        self._phase_one()

    def on_disconnect(self):
        self.connected = False  # Reset flag when disconnected
        print("Disconnected from the server")

    def on_environment(self, data):
        print("Environment data received:", data)
        if data == 'environment':
            self.emit_environment_data()
        if data == "next":
            self.environment_connection.next()

    def sync(self):
        self.emit_environment_data()

    def on_set(self, data):
        self.environment_connection.set(data)

    def on_request(self, data):
        print("on_request method entered with data:", data)
        if data == 'environment':
            self.emit_environment_data()
        if data == "id":
            pass

    def connect(self):
        try:
            self.sio.on('connect', self.on_connect)
            self.sio.on('disconnect', self.on_disconnect)
            self.sio.on('environment', self.on_environment)
            self.sio.on('request', self.on_request)
            self.sio.on('gui', self.on_set)
            self.sio.on('data', self.on_set)
            self.sio.connect(self.url)

        except socketio.exceptions.ConnectionError as e:
            print(f"Connection failed: {e}")

    def disconnect(self):
        self.sio.disconnect()

    def emit_environment_data(self):
        # Fetch the environment data and emit it
        env_data = self.environment_connection.environment.to_dict()
        self.send_message('gui', env_data)

    def send_message(self, event: str, data: Dict):
        # Check if the data is serializable
        if not self._check_serialize(data):
            return

        if self.connected:  # Check if connected before emitting
            self.sio.emit(event, data)
        else:
            print("Cannot send message, client is not connected.")

    def _check_serialize(self, data: Dict) -> bool:
        # Check if the data is serializable
        try:
            # Try to serialize the data. This will raise a TypeError if the data is not serializable.
            json.dumps(data)
            return True  # Data is serializable
        except TypeError as e:
            print(f"Data is not serializable: {e}")
            return False  # Data is not serializable
