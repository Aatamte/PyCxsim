import os
import logging
from flask import Flask, send_from_directory
from typing import Any, Optional


class PyCxsimFrontend:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.logger = self._setup_logging()

        build_dir = os.path.join(os.path.dirname(__file__), 'build')
        self.app = Flask(__name__, static_folder=build_dir, static_url_path='')
        self.add_routes()

    def _setup_logging(self):
        """Set up logging for the application."""
        logger = logging.getLogger('PyCxsimFrontend')
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def add_routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/<path:path>', 'serve_static', self.serve_static)

    def index(self):
        if self.verbose:
            self.logger.info("Serving index.html")
        return send_from_directory(self.app.static_folder, 'index.html')

    def serve_static(self, path):
        if self.verbose:
            self.logger.info(f"Serving static file: {path}")
        return send_from_directory(self.app.static_folder, path)

    def run(self, host: Optional[str] = None, port: Optional[int] = None,
            debug: Optional[bool] = None, load_dotenv: bool = True, **options: Any) -> None:
        """
        Runs the Flask application.

        :param host: The hostname to listen on. Set this to '0.0.0.0' to have the server available externally.
        :param port: The port of the webserver.
        :param debug: If given, enable or disable debug mode.
        :param load_dotenv: Load the nearest .env and .flaskenv files to set environment variables.
        :param options: Additional options passed to `flask run`.
        """
        if self.verbose:
            self.logger.info("Starting Flask application")
        self.app.run(host=host, port=port, debug=debug, load_dotenv=load_dotenv, **options)


if __name__ == '__main__':
    PyCxsimFrontend().run()


