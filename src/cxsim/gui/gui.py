import logging
from flask import Flask, send_from_directory, request, Response
from flask_socketio import SocketIO
from typing import Optional, Any, Dict

# core methods to update react with the correct info

#


from flask import Flask, send_from_directory
import os

class GUI(Flask):
    def __init__(self, build_path=None):
        super(GUI, self).__init__(__name__, static_folder=build_path, static_url_path='')
        if build_path:
            self.build_dir = build_path
        else:
            self.build_dir = os.path.join(os.path.dirname(__file__), 'build')
        self.static_folder = self.build_dir

    def serve(self, host='localhost', port=8100):
        print(f"Serving from {self.build_dir}")

        # Route to serve the index.html
        @self.route('/')
        def serve_index():
            return send_from_directory(self.static_folder, 'index.html')

        # Generic route to serve all static files and assets
        @self.route('/<path:path>')
        def serve_static(path):
            # Attempt to serve the file if it exists
            if os.path.exists(os.path.join(self.static_folder, path)):
                return send_from_directory(self.static_folder, path)
            # Fallback to index.html, which allows SPA routing to work
            else:
                return serve_index()

        self.run(host=host, port=port, threaded=True)


class GUIServer:
    def __init__(self, verbose=False, dev_mode=False):
        self.verbose = verbose
        self.dev_mode = dev_mode

        self.connected_guis = set()
        self.connected_environments = set()

        self.logger = self._setup_logging()
        self.app, self.socketio = self._setup_app_and_socketio()

        self.add_routes()
        self.add_socketio_events()

        self.set_up_complete: bool = False

    def set_up(self):
        print("setting up the connection")
        self.send_connection_statuses()
        self.send("environment", "full_refresh", {})
        self.send("gui", "initial handshake", {"content": "hello"})

    def get_connections_status(self):
        return {
            "gui_connection": "open" if self.has_connected_gui else "closed",
            "environment_connection": "open" if self.has_connected_environment else "closed"
        }

    def send_connection_statuses(self):
        print("sending connection statuses")
        self.send("gui", "kv_storage", self.get_connections_status())
        self.send("environment", "kv_storage", self.get_connections_status())

    def get_kv_storage(self):
        return {
            **self.get_connections_status(),
        }

    @property
    def is_ready_for_set_up(self):
        return len(self.connected_environments) >= 1 and len(self.connected_guis) >= 1

    @property
    def has_connected_gui(self):
        return len(self.connected_guis) >= 1

    @property
    def has_connected_environment(self):
        return len(self.connected_environments) >= 1

    def _setup_logging(self):
        logger = logging.getLogger('PyCxSim GUI Server')
        level = logging.DEBUG if self.verbose else logging.INFO
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _setup_app_and_socketio(self):
        build_dir = os.path.join(os.path.dirname(__file__), 'build')
        print(build_dir)
        app = Flask(__name__, static_folder=build_dir if not self.dev_mode else None, static_url_path='')
        socketio = SocketIO(app, cors_allowed_origins="*")
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        print(f"Static files are being served from: {build_dir}")  # Print statement added
        return app, socketio

    def add_socketio_events(self):
        @self.socketio.on('connect')
        def handle_connect():
            self._handle_connect(request.sid)

        @self.socketio.on('disconnect')
        def handle_disconnect():
            self._handle_disconnect(request.sid)

        @self.socketio.on('register_client')
        def handle_report_type(data):
            print("registering client...")
            self._handle_register_client(request.sid, data)

        @self.socketio.on('data')
        def handle_data(data):
            self._handle_data(data)

    def _handle_server_request(self, data):\
        print("internal_sever_request: ", data)

    def _handle_data(self, data):
        header = data.get("header")

        self._log_info(f'_handle data: {data}')
        source = data.get('source')

        if source == "environment":
            self.send("gui", data["header"], data["content"])
        elif source == "GUI":
            self.send("environment", data["header"], data["content"])

    def _handle_connect(self, client_id):
        self.socketio.emit('request', "id", room=client_id)
        self._log_info(f'Client connected: {client_id}')
        self.send_connection_statuses()

    def _handle_disconnect(self, client_id):
        self._remove_client(client_id)
        self._log_info(f'Client disconnected: {client_id}')
        self.set_up_complete = False
        self.send_connection_statuses()

    def _handle_register_client(self, client_id, data):
        client_type = data.get('type')
        if client_type == "environment":
            self.connected_environments.add(client_id)
            self._log_info(f'Client {client_id} registered as environment')
        elif client_type == "gui":
            self.connected_guis.add(client_id)
            self._log_info(f'Client {client_id} registered as GUI')

        if self.is_ready_for_set_up:
            self.set_up()

    def send(self, location: str, header: str, data: Dict):
        msg = {
            "header": header,
            "content": data
        }

        if location == "environment":
            for client_id in self.connected_environments:
                self.socketio.emit("data", msg, room=client_id)
        elif location == "gui":
            for client_id in self.connected_guis:
                self.socketio.emit("data", msg, room=client_id)
        else:
            raise RuntimeError("location is invalid")

    def add_routes(self):
        if not self.dev_mode:
            self.app.add_url_rule('/', 'index', self.index)
            self.app.add_url_rule('/<path:path>', 'serve_static', self.serve_static)

    def index(self):
        self._log_info("Serving index.html")
        return send_from_directory(self.app.static_folder, 'index.html')

    def serve_static(self, path):
        self._log_info(f"Serving static file: {path}")
        return send_from_directory(self.app.static_folder, path)

    def _remove_client(self, client_id):
        self.connected_guis.discard(client_id)
        self.connected_environments.discard(client_id)

        self._log_info(f'Client {client_id} removed from all sets')

    def _log_info(self, message):
        if self.verbose:
            self.logger.info(message)

    def start(self, host: Optional[str] = None, port: Optional[int] = None,
            debug: Optional[bool] = None, load_dotenv: bool = True, **options: Any):
        self._log_info(f"Starting Flask application with dev_mode={self.dev_mode} and verbose={self.verbose}")
        import threading
        import webbrowser
        if not self.dev_mode:
            url = f"http://{host}:{port}"
            threading.Thread(target=lambda: webbrowser.open(url)).start()
        self.app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


if __name__ == '__main__':
    server = SimpleGUIServer()

    server.start(host='localhost', port=8765)



