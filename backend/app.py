# backend/app.py
from flask import Flask
from flask_cors import CORS
from routes.bill_routes import bill_routes
import logging
logging.basicConfig(level=logging.DEBUG)


# app = Flask(__name__)
# CORS(app)
# #CORS(app, origins=["http://localhost:3000"], supports_credentials=True)  # ✅ only this one
# # CORS(
# #     app,
# #     origins=["http://localhost:3000"],
# #     supports_credentials=True,
# #     allow_headers=["Content-Type", "X-gemini-api-key"]  # ✅ must include custom header
# # )

# # CORS(
# #     app,
# #     resources={r"/api/*": {"origins": "http://localhost:3000"}},
# #     supports_credentials=True,
# #     allow_headers=["Content-Type", "Access-Control-Allow-Origin"],
# #     methods=["GET", "POST", "OPTIONS"]  # Needed for preflight!
# # )

# app.register_blueprint(bill_routes)

# @app.route("/")
# def home():
#     return {"message": "Hello from Flask!"}

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)



# '''
# from flask import Flask, jsonify
# from flask_cors import CORS
# from routes import bill_routes

# app = Flask(__name__)
# CORS(app, origins=["http://localhost:3000"], supports_credentials=True)  # ✅ only this one

# # Register API routes
# app.register_blueprint(bill_routes)

# @app.route("/")  # ✅ Health check route
# def home():
#     return jsonify({"message": "Welcome to Athena AI Backend!"})

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)
# '''

app = Flask(__name__)

# ✅ Simple and clean CORS setup
CORS(
    app,
    resources={r"/*": {"origins": "*"}},
)

app.register_blueprint(bill_routes)

@app.route("/")
def home():
    return {"message": "Hello from Flask!"}

if __name__ == "__main__":
    app.run(debug=True, port=5000)
