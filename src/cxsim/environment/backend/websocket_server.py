import asyncio
import websockets


class WebSocketServer:
    def __init__(self, host='localhost', port=8765):
        self.host = host
        self.port = port

    async def echo(self, websocket, path):
        async for message in websocket:
            print(f"Received message: {message}")
            await websocket.send(f"Echo: {message}")

    async def start(self):
        async with websockets.serve(self.echo, self.host, self.port):
            print(f"WebSocket Server started at ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run the server indefinitely

    def run(self):
        asyncio.run(server.start())


if __name__ == "__main__":
    server = WebSocketServer()
    server.run()

