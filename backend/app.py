from flask import Flask, send_from_directory
from flask_cors import CORS
from config.db import init_db
from routes.auth import auth_bp
from routes.results import results_bp
from routes.students import students_bp
from routes.subjects import subjects_bp
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

CORS(app, supports_credentials=True, origins="*")

# Serve frontend HTML files
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), '..', 'frontend')

@app.route('/')
def index():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/login')
def login_page():
    return send_from_directory(FRONTEND_DIR, 'login.html')

@app.route('/admin')
def admin_page():
    return send_from_directory(FRONTEND_DIR, 'admin.html')

@app.route('/student')
def student_page():
    return send_from_directory(FRONTEND_DIR, 'student.html')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(results_bp, url_prefix="/api/results")
app.register_blueprint(students_bp, url_prefix="/api/students")
app.register_blueprint(subjects_bp, url_prefix="/api/subjects")

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
