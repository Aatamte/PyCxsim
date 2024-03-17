import asyncio
import websockets
import threading
import json


def serialize(data):
    try:
        return json.dumps(data)
    except TypeError as e:
        print(f"Failed to serialize data: {e}")
        return None


class WebSocketServer:
    def __init__(self, environment, host='localhost', port=8765):
        self.environment_manager: EnvironmentManager = EnvironmentManager(environment)
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = None
        self.environment = environment

    def step(self):
        # send over core data
        print("sending data over websocket")

        # update agents
        data = self.environment_manager.update_agents()
        self.send_to_all_clients(data)

        # update artifacts
        data = self.environment_manager.update_artifacts()
        print(data)
        self.send_to_all_clients(data)

        data = self.environment_manager.step_variables

        self.send_to_all_clients(data)

    def compile(self):
        data = self.environment_manager.get_env_core_variables()
        self.send_to_all_clients(data)

        self.initialize()

    def initialize(self):
        data = self.environment_manager.init_artifacts()
        self.send_to_all_clients(data)

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)

    async def process_message(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                # Decode the message from JSON format
                try:
                    decoded_message = json.loads(message)
                except json.JSONDecodeError:
                    print(f"Received non-JSON message: {message}")
                    continue  # Skip this message
                response = self.environment_manager.handle_message(decoded_message)
                self.send_to_all_clients(response)

        finally:
            await self.unregister(websocket)

    async def start(self):
        async with websockets.serve(self.process_message, self.host, self.port):
            print(f"WebSocket Server started at ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run the server indefinitely

    def run_in_thread(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start())

    def run(self):
        thread = threading.Thread(target=self.run_in_thread)
        thread.start()

    async def _send_to_all_clients(self, data):
        if self.clients:  # Check if there are any connected clients
            await asyncio.gather(*(client.send(data) for client in self.clients))

    def send_to_all_clients(self, data):
        data_list = []
        if data is None:
            return
        elif isinstance(data, list):
            data_list = data
        else:
            data_list.append(data)

        for d in data_list:
            # Serialize the data to a JSON string
            try:
                _data = json.dumps(d)
            except TypeError as e:
                print(f"Failed to serialize data to JSON: {e}")
                return

            if self.loop is not None:
                asyncio.run_coroutine_threadsafe(self._send_to_all_clients(_data), self.loop)

