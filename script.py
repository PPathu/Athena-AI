import json
import psycopg2
from keys import userkey
from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()

if load_dotenv(dotenv_path):
    print("SUCCESS: .env loaded")
else:
    print("ERROR: .env not loaded")
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {DATABASE_URL}")

# Load JSON Data
with open("data.json", "r") as file:
    bills_data = json.load(file)

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="scrapedfilesdatabase",
    user = userkey,
    host="localhost",
    password="yourpassword"  # Replace with your actual password
)
cur = conn.cursor()

# SQL Insert Query
insert_query = """
    INSERT INTO bills (billNumber, billId, billStatusDate, billStatus, billTitle, billDescription)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (billId) DO NOTHING;
"""

# Insert Data
for bill in bills_data:
    cur.execute(insert_query, (
        bill["billNumber"],
        bill["billId"],
        bill["billStatusDate"],
        bill["billStatus"],
        bill["billTitle"],
        bill["billDescription"]
    ))


conn.commit()
cur.close()
conn.close()

print("Data inserted successfully!")

