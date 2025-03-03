import json
import psycopg2
from dotenv import load_dotenv, find_dotenv
import os
#load .env variables
dotenv_path = find_dotenv()
if load_dotenv(dotenv_path):
    print("SUCCESS: .env loaded")
else:
    print("ERROR: .env not loaded")
#get supabase database url from .env file
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Database URL: {DATABASE_URL}")
#load json bill data
with open("data.json", "r") as file:
    bills_data = json.load(file)
#connect to supabase
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()
#check that the `bills` table exists
cur.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        billNumber TEXT NOT NULL,
        billId TEXT PRIMARY KEY,
        billStatusDate TIMESTAMP,
        billStatus TEXT,
        billTitle TEXT,
        billDescription TEXT
    );
""")
insert_query = """
    INSERT INTO bills (billNumber, billId, billStatusDate, billStatus, billTitle, billDescription)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (billId) DO NOTHING;
"""
#insert the data
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
print("Data was successfully inserted into Supabase database")