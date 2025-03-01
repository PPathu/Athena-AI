import json
import psycopg2
import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

#load .env variables
dotenv_path = find_dotenv()
if load_dotenv(dotenv_path):
    print("success: .env loaded")
else:
    print("error: .env not loaded")

#get database URL from .env file
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("error: DATABASE_URL not found in .env file")

print(f"database URL: {DATABASE_URL}")

try:
    with open("data.json", "r") as file:
        bills_data = json.load(file)
    print(f"loaded {len(bills_data)} bills from data.json")
except Exception as e:
    raise RuntimeError(f"error: loading JSON file: {e}")

#print(json.dumps(bills_data[:5], indent=4))

#connect to supabase
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    print("connected to Supabase")
except Exception as e:
    raise RuntimeError(f"error connecting to database: {e}")

#make sure the table exists with correct column names
try:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS enhanceddata (
            id SERIAL PRIMARY KEY,
            bill_number TEXT UNIQUE NOT NULL,
            bill_id TEXT UNIQUE NOT NULL,
            bill_status_date TIMESTAMP,
            bill_status TEXT,
            title TEXT NOT NULL,  -- FIXED: Using "title" instead of "bill_title"
            bill_description TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    print("table `enhanceddata` checked/created")
except Exception as e:
    raise RuntimeError(f"error creating table: {e}")

#insert query using the correct column names
insert_query = """
    INSERT INTO enhanceddata (bill_number, bill_id, bill_status_date, bill_status, title, bill_description)
    VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (bill_id) DO NOTHING;
"""

#insert bills into database
for bill in bills_data:
    try:
        bill_number = bill.get("billNumber") or bill.get("bill_number")
        bill_id = str(bill.get("billId") or bill.get("bill_id")) 
        bill_status_date = bill.get("billStatusDate") or bill.get("statusDate")
        bill_status = str(bill.get("billStatus") or bill.get("status", ""))
        bill_title = bill.get("billTitle") or bill.get("title")
        bill_description = bill.get("billDescription") or bill.get("description")

        #convert date if present
        if bill_status_date:
            try:
                bill_status_date = datetime.strptime(bill_status_date, "%Y-%m-%d")
            except ValueError:
                print(f"invalid date format: {bill_status_date}")
                bill_status_date = None

        #make sure required fields are present
        if not bill_number:
            print(f"missing bill_number: {bill}")
        if not bill_id:
            print(f"missing bill_id: {bill}")
        if not bill_title:
            print(f"missing title: {bill}")
        
        #skip if required fields are missing
        if not bill_number or not bill_id or not bill_title:
            continue

        #insert data into database
        cur.execute(insert_query, (
            bill_number, bill_id, bill_status_date, bill_status, bill_title, bill_description
        ))
        conn.commit()  #commit after each insert
        print(f"inserted bill {bill_number} ({bill_id})")

    except Exception as e:
        print(f"error inserting bill {bill_number}: {e}")
        print(f"query data: {bill_number}, {bill_id}, {bill_status_date}, {bill_status}, {bill_title}, {bill_description}")
        conn.rollback()

cur.close()
conn.close()
print("data successfully inserted into Supabase")
