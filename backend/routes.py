from flask import Blueprint, jsonify
from database import get_db_connection

bill_routes = Blueprint("bill_routes", __name__)

@bill_routes.route("/api/bills", methods=["GET"])
def get_bills():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT bill_id, title, description, status FROM enhanceddata;")
    bills = cur.fetchall()

    cur.close()
    conn.close()

    return jsonify([{"bill_id": b[0], "title": b[1], "description": b[2], "status": b[3]} for b in bills])
