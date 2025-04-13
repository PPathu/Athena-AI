# from flask import Blueprint, request, jsonify
# # ❌ REMOVE this decorator if you're already using global CORS in app.py
# # from flask_cors import cross_origin  

# bill_routes = Blueprint("bill_routes", __name__)


# # ❌ REMOVE this if you already have: CORS(app) in app.py
# # @cross_origin(origin='http://localhost:3000', supports_credentials=True)
# # @bill_routes.route("/api/chat", methods=["POST"])
# @bill_routes.route("/api/chat", methods=["POST"])
# def chat():
#     print("💡 /api/chat HIT")
#     print("Request headers:", dict(request.headers))
#     return jsonify({"answer": "Test answer from backend."})


# '''
# from flask import Blueprint, jsonify
# from database import get_db_connection

# bill_routes = Blueprint("bill_routes", __name__)

# @bill_routes.route("/bills", methods=["GET"])
# def get_bills():
#     conn = get_db_connection()
#     cur = conn.cursor()

#     cur.execute("SELECT bill_id, title, description, status FROM enhanceddata;")
#     bills = cur.fetchall()

#     cur.close()
#     conn.close()

#     return jsonify([{"bill_id": b[0], "title": b[1], "description": b[2], "status": b[3]} for b in bills])
# '''


from flask import Blueprint, request, jsonify

bill_routes = Blueprint("bill_routes", __name__)

@bill_routes.route("/api/chat", methods=["POST"])
def chat():
    print("💡 /api/chat HIT")
    print("Request headers:", dict(request.headers))
    return jsonify({"answer": "Test answer from backend."})
