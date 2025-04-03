from flask import Flask, jsonify
from flask_cors import CORS
from routes import bill_routes
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Register API routes
app.register_blueprint(bill_routes)

@app.route("/")  # ✅ Add this route to prevent 404
def home():
    return jsonify({"message": "Welcome to Athena AI Backend!"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
