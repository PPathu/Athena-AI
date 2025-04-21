from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from routes import bill_routes
import os
from dotenv import load_dotenv

# Load environment variables
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Frontend dist directory path
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'dist'))

app = Flask(__name__, static_folder=None)
CORS(app)  # Enable CORS for frontend communication

# Register API routes without prefix since routes already have /api prefix
app.register_blueprint(bill_routes)

@app.route("/")  # Home route
def home():
    return send_from_directory(frontend_dir, 'index.html')

# Serve static files from the frontend build
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(os.path.join(frontend_dir, 'static'), path)

# Serve all other frontend assets
@app.route('/<path:path>')
def serve_any(path):
    if os.path.exists(os.path.join(frontend_dir, path)):
        return send_from_directory(frontend_dir, path)
    else:
        return send_from_directory(frontend_dir, 'index.html')

if __name__ == "__main__":
    app.run(debug=True, port=8000)
