import os
import logging
from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO
from typing import Optional, Any


class GUI:
    def __init__(self, verbose=False, dev_mode=False):
        self.verbose = verbose
        self.dev_mode = dev_mode

        self.connected_guis = set()
        self.connected_environments = set()

        self.logger = self._setup_logging()
        self.app, self.socketio = self._setup_app_and_socketio()

        self.add_routes()
        self.add_socketio_events()

        self.phase_one_completed: bool = False
        self.phase_two_completed: bool = False
        self.phase_three_completed: bool = False

        self.set_up_complete: bool = False

    @property
    def is_ready_for_set_up(self):
        return len(self.connected_environments) >= 1 and len(self.connected_guis) >= 1 and not self.set_up_complete

    def set_up(self):
        print("running phases")
        self.phase_one_completed = True

    def _setup_logging(self):
        logger = logging.getLogger('PyCxsimFrontend')
        level = logging.DEBUG if self.verbose else logging.INFO
        logger.setLevel(level)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _setup_app_and_socketio(self):
        build_dir = os.path.join(os.path.dirname(__file__), 'build')
        app = Flask(__name__, static_folder=build_dir if not self.dev_mode else None, static_url_path='')
        socketio = SocketIO(app, cors_allowed_origins="*")
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
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

        for event in ['environment', 'gui', 'data']:
            self.socketio.on(event)(self._handle_custom_event)

    def _handle_connect(self, client_id):
        self.socketio.emit('request', "id", room=client_id)
        self._log_info(f'Client connected: {client_id}')

    def _handle_disconnect(self, client_id):
        self._remove_client(client_id)
        self._log_info(f'Client disconnected: {client_id}')

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

    def _log_info(self, message):
        if self.verbose:
            self.logger.info(message)

    def emit_event(self, event, data):
        if event == 'environment':
            for client_id in self.connected_environments:
                self.socketio.emit(event, data, room=client_id)
        elif event in ['gui', 'data']:
            for client_id in self.connected_guis:
                self.socketio.emit(event, data, room=client_id)

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

    def _handle_custom_event(self, data):
        event = request.event['message']
        self._log_info(f'Received data on {event}: {data}')
        self.emit_event(event, data)

    def _remove_client(self, client_id):
        self.connected_guis.discard(client_id)
        self.connected_environments.discard(client_id)
        self._log_info(f'Client {client_id} removed from all sets')

    def run(self, host: Optional[str] = None, port: Optional[int] = None,
            debug: Optional[bool] = None, load_dotenv: bool = True, **options: Any):
        self._log_info(f"Starting Flask application with dev_mode={self.dev_mode} and verbose={self.verbose}")
        import threading
        import webbrowser
        if not self.dev_mode:
            url = f"http://{host}:{port}"
            threading.Thread(target=lambda: webbrowser.open(url)).start()
        self.app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)

    def reset_phases(self):
        self.phase_one_completed: bool = False
        self.phase_two_completed: bool = False
        self.phase_three_completed: bool = False


if __name__ == '__main__':
    GUI(verbose=True, dev_mode=True).run(host='localhost', port=8765)



