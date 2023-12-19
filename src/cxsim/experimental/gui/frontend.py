import os
from flask import Flask, send_from_directory


class PyCxsimFrontend:
    def __init__(self):
        build_dir = os.path.join(os.path.dirname(__file__), 'build')
        self.app = Flask(__name__, static_folder=build_dir, static_url_path='')
        self.add_routes()


    def add_routes(self):
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/<path:path>', 'serve_static', self.serve_static)

    def index(self):
        return send_from_directory(self.app.static_folder, 'index.html')

    def serve_static(self, path):
        return send_from_directory(self.app.static_folder, path)

    def run(self):
        self.app.run()


if __name__ == '__main__':
    PyCxsimFrontend().run()


