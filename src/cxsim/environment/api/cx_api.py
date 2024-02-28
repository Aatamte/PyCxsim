from flask import Flask, request, jsonify
from cxsim.environment.database.cx_database import CxDatabase
import threading
from typing import Union


class CxAPI:
    def __init__(self, db: Union[str, CxDatabase] = None):
        self.app = Flask(__name__)
        if isinstance(db, CxDatabase):
            self.database = db
        elif isinstance(db, str):
            self.database = CxDatabase(db)
            self.database.connect()
        else:
            self.database = CxDatabase()
            self.database.connect()

        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def home():
            return jsonify({"message": "Welcome to CxAPI!"})

        @self.app.route('/tables/<table_name>', methods=['GET'])
        def get_table_data(table_name):
            try:
                # Fetch data from the specified table using the get() method
                data = self.database[table_name].get()
                return jsonify(data), 200
            except KeyError:
                # If the specified table is not found in the database
                return jsonify({"error": f"Table '{table_name}' not found."}), 404
            except Exception as e:
                # Handle other exceptions, such as potential errors in the get() method
                return jsonify({"error": str(e)}), 500

    def setup_teardown(self):
        @self.app.teardown_appcontext
        def teardown_db(exception=None):
            if hasattr(self, 'database'):
                self.database.close()

    def run(self, host='localhost', port=8000, debug=True):
        def run_app():
            self.app.run(host=host, port=port, debug=debug, use_reloader=False)

        # Create a thread to run the Flask application
        flask_thread = threading.Thread(target=run_app)
        flask_thread.start()
