import time

import socketio
from typing import Dict

import json


class GUIServerConnection:
    def __init__(self, environment, host='localhost', port=8765):
        self.sio = socketio.Client(logger=True, engineio_logger=True, reconnection=False)
        self.url = f"http://{host}:{port}"
        self.environment = environment

        self.connected = False
        self.has_registered = False

        # secure connection to the server
        self.phase_one: bool = False

        # pass environment metadata to the server
        self.phase_two: bool = False

        self.phase_three: bool = False

    def full_refresh(self):
        data = self.environment.metadata
        print(data)
        self.send_message("environment", data)

        agent_data = self.environment.agent_metadata
        #self.send_message("agents", agent_data)

        artifact_data = self.environment.artifact_metadata
        #self.send_message("artifacts", artifact_data)

    def on_connect(self):
        self.connected = True  # Set flag to True when connected
        self.sio.emit("register_client", {'type': 'environment'})

    def on_disconnect(self):
        self.connected = False  # Reset flag when disconnected
        print("Disconnected from the server")

    def on_data(self, data):
        print(data)
        header = data["header"]
        content = data["content"]
        print(header, content)
        if header == "full_refresh":
            self.full_refresh()
        elif header == "action":
            self.environment.handle_gui_event(content)
        else:
            print(f"did not recognize header: {header}")

    def connect(self):
        try:
            self.sio.on('connect', self.on_connect)
            self.sio.on('disconnect', self.on_disconnect)
            self.sio.on('data', self.on_data)
            self.sio.connect(self.url)

        except socketio.exceptions.ConnectionError as e:
            print(f"Connection failed: {e}")

    def disconnect(self):
        self.sio.disconnect()

    def send_message(self, header: str, data: Dict):
        # Check if the data is serializable
        if not self._check_serialize(data):
            return

        msg = {
            "header": header,
            "content": data,
            "source": "environment"
        }

        if self.connected:  # Check if connected before emitting
            self.sio.emit("data", msg)
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
