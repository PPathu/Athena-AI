# backend/app.py
from flask import Flask
from flask_cors import CORS
from routes.bill_routes import bill_routes
import logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

CORS(
    app,
    origins=["http://localhost:3000"],
    supports_credentials=True,
    allow_headers=["Content-Type", "x-gemini-api-key"],
    methods=["GET", "POST", "OPTIONS"],
    send_wildcard=True 
)


app.register_blueprint(bill_routes)
@app.route("/")
def home():
    return {"message": "Hello from Flask!"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
