import os
import sys
from dotenv import load_dotenv
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Load .env if present (local dev). In Docker, real env vars are injected by compose.
_env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '.env')
if os.path.exists(_env_path):
    load_dotenv(_env_path)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.config import Config
from database.connection import DatabaseConnection
from database.init_db import initialize_database
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp
from routes.project_routes import project_bp
from routes.task_routes import task_bp
from routes.expense_routes import expense_bp
from routes.notification_routes import notification_bp
from routes.reports_routes import report_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

app.register_blueprint(auth_bp)
app.register_blueprint(user_bp)
app.register_blueprint(project_bp)
app.register_blueprint(task_bp)
app.register_blueprint(expense_bp)
app.register_blueprint(notification_bp)
app.register_blueprint(report_bp)

if not os.path.exists(Config.UPLOAD_FOLDER):
    os.makedirs(Config.UPLOAD_FOLDER)


@app.route('/api/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(Config.UPLOAD_FOLDER, filename)


@app.route('/api/health')
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Task & Expense Management System API'})


@app.errorhandler(404)
def not_found(error):
    return jsonify({'message': 'Resource not found', 'success': False}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'message': 'Internal server error', 'success': False}), 500


if __name__ == '__main__':
    try:
        initialize_database()
    except Exception as e:
        print(f"Warning: Database initialization error: {e}")
        print("Make sure SQL Server is running and accessible.")

    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=int(os.environ.get('PORT', 5000)),
        debug=Config.DEBUG
    )
