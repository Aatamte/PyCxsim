import threading
from flask import Flask
from flask_socketio import SocketIO, emit
from typing import Union

from cxsim.environment.database.cx_database import CxDatabase

import json
from datetime import datetime


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CxSocket:
    def __init__(
            self,
            environment,
            host='localhost',
            port=8100,
            db: Union[str, CxDatabase] = None
    ):
        self.environment = environment
        self.app = Flask(__name__)
        self.socketio = SocketIO(self.app, cors_allowed_origins='*')  # Allow all origins
        self.host = host
        self.port = port

        if isinstance(db, CxDatabase):
            self.database = db
        elif isinstance(db, str):
            self.database = CxDatabase(db)
            self.database.connect()
        else:
            self.database = CxDatabase()
            self.database.connect()

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

        @self.socketio.on('data_send')
        def handle_data_send(payload):
            table_name = payload['table_name']
            content = payload['content']
            # Process the received data here
            self.environment.handle_button_event(content["value"])

    def send_message(self, message, room: str = None):
        self.socketio.emit(f'data_update', message)

    def send_table(self, table_name: str):
        content = self.database[table_name].get()
        msg = {
            "table_name": table_name,
            "content": content
        }

        self.socketio.emit('data_update', msg)

    def _run(self):
        self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True)

    def run(self):
        threading.Thread(target=self._run).start()

