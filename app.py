from flask import Flask, jsonify
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

def get_db_connection():
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST")
    )
    return conn

@app.route('/bills', methods=['GET'])
def get_bills():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT billNumber, billId, billStatusDate, billStatus, billTitle, billDescription FROM bills;")
    bills_data = cur.fetchall()
    cur.close()
    conn.close()

    bills = [{
        "billNumber": b[0],
        "billId": b[1],
        "billStatusDate": b[2],
        "billStatus": b[3],
        "billTitle": b[4],
        "billDescription": b[5]
    } for b in bills_data]

    return jsonify(bills)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
