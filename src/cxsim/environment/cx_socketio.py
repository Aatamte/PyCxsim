import threading
import time

from flask import Flask
from flask_socketio import SocketIO, emit
from typing import Union
import json
from datetime import datetime

from cxsim.agents.agent import Agent
from cxsim.environment.database.cx_database import CxDatabase


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
            print('Socket connected')
            self.sync_environment()
            self.database["sqlite_master"].emit(self.socketio)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            print('Socket disconnected')

        @self.socketio.on('message')
        def handle_message(message):
            # Process the message here
            response = "none"
            self.socketio.emit('response', response)

        @self.socketio.on('data_send')
        def handle_data_send(payload):
            content = payload['content']
            # Process the received data here
            self.environment.handle_button_event(content["value"])

    def sync_agent(self, agent: Agent):
        self.database["cxagents"].upsert(
            name=agent.name,
            x_pos=agent.x_pos,
            y_pos=agent.y_pos,
            parameters=agent.params,
            inventory=agent.inventory.inventory,
            messages=agent.io.text.full_messages,
            past_actions=agent.action_history
        )
        self.database["cxagents"].emit(self.socketio)

    def sync_environment(self):
        self.database["cxmetadata"].upsert(key="name", value=self.environment.name)
        self.database["cxmetadata"].upsert(key="max_steps", value=self.environment.max_steps)
        self.database["cxmetadata"].upsert(key="max_episodes", value=self.environment.max_episodes)
        self.database["cxmetadata"].upsert(key="n_artifacts", value=self.environment.n_artifacts)
        self.database["cxmetadata"].upsert(key="n_agents", value=self.environment.n_agents)
        self.database["cxmetadata"].upsert(key="x_size", value=self.environment.gridworld.x_size)
        self.database["cxmetadata"].upsert(key="y_size", value=self.environment.gridworld.y_size)
        self.database["cxmetadata"].upsert(key="current_episode", value=self.environment.current_episode)
        self.database["cxmetadata"].upsert(key="current_step", value=self.environment.current_step)
        self.database["cxmetadata"].upsert(key="current_status", value=self.environment.get_status)

        # Check if agent_queue is not empty before accessing the first element
        next_agent_name = self.environment.agent_queue[0].name if self.environment.agent_queue else "None"
        self.database["cxmetadata"].upsert(key="next_agent", value=next_agent_name)
        self.database["cxmetadata"].emit(self.socketio)

        for agent in self.environment.agents:
            self.sync_agent(agent)

        self.sync_gridworld()

        self.upload_all_tables()

    def sync_gridworld(self):
        block_representation = self.environment.gridworld.get_blocks()

        entries = [
            {
                "position": block["position"],
                "color": block["color"],
                "content": block["content"],
                "can_occupy": block["can_occupy"],
                "is_goal": block["is_goal"]
            }
            for block in block_representation
        ]

        self.database["cxgridworld"].upsert_many(entries)

    def upload_all_tables(self):
        for table_str in list(self.database.tables.keys()):
            self.database[table_str].emit(self.socketio)

    def send_message(self, message, room: str = None):
        self.socketio.emit(f'data_update', message)

    def _run(self):
        self.socketio.run(self.app, host=self.host, port=self.port, allow_unsafe_werkzeug=True)

    def run(self):
        threading.Thread(target=self._run).start()

