import asyncio
import websockets
import threading
import json


class WebSocketServer:
    def __init__(self, environment, host='localhost', port=8765):
        self.environment_wrapper = EnvironmentWrapper(environment)
        self.host = host
        self.port = port
        self.clients = set()
        self.loop = None

    def step(self):
        # send over core data
        data = self.environment_wrapper.get_env_core_variables()

        self.send_to_all_clients(data)

    def compile(self):
        data = self.environment_wrapper.get_agent_names
        self.send_to_all_clients(data)

    async def register(self, websocket):
        self.clients.add(websocket)

    async def unregister(self, websocket):
        self.clients.remove(websocket)

    async def echo(self, websocket, path):
        await self.register(websocket)
        try:
            async for message in websocket:
                print(f"Received message: {message}")
        finally:
            await self.unregister(websocket)

    async def start(self):
        async with websockets.serve(self.echo, self.host, self.port):
            print(f"WebSocket Server started at ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run the server indefinitely

    def run_in_thread(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.start())
        self.loop.close()

    def run(self):
        thread = threading.Thread(target=self.run_in_thread)
        thread.start()

    async def _send_to_all_clients(self, data):
        if self.clients:  # Check if there are any connected clients
            await asyncio.wait([client.send(data) for client in self.clients])

    def send_to_all_clients(self, data):
        # Serialize the data to a JSON string
        try:
            _data = json.dumps(data)
        except TypeError as e:
            print(f"Failed to serialize data to JSON: {e}")
            return

        if self.loop is not None:
            asyncio.run_coroutine_threadsafe(self._send_to_all_clients(_data), self.loop)


class EnvironmentWrapper:
    def __init__(self, environment):
        self.environment = environment

    def compile(self):
        # send over core data
        pass

    @property
    def check_environment_status(self):

        return {

        }

    def get_grid_size(self):
        pass

    @property
    def get_agent_names(self):
        return {
            "agent_names": self.environment.agents
        }

    def get_env_core_variables(self):
        return {
            "episode": self.environment.current_episode,
            "step": self.environment.current_step,
            "max_episodes": self.environment.max_episodes,
            "max_steps": self.environment.max_steps
        }






if __name__ == "__main__":
    server = WebSocketServer(None)  # Replace None with an actual environment object if needed
    server.run()


