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
    with open("NEWdata.json", "r") as file:
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
        DROP TABLE IF EXISTS enhanceddata CASCADE;
        CREATE TABLE enhanceddata (
            id SERIAL PRIMARY KEY,
            doc_type TEXT,
            bill_id TEXT UNIQUE NOT NULL,
            bill_number TEXT NOT NULL,
            session TEXT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT,
            status_date TIMESTAMP,
            last_action TEXT,
            last_action_date TIMESTAMP,
            url TEXT,
            pdf_link TEXT,
            txt_link TEXT,
            amendments TEXT,
            amendment_links TEXT,
            see_also TEXT,
            history TEXT,
            created_at TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    print("table `enhanceddata` checked/created")
except Exception as e:
    raise RuntimeError(f"error creating table: {e}")

#insert query using the correct column names
insert_query = """
    INSERT INTO enhanceddata (
        doc_type, bill_id, bill_number, session, title, description, status, status_date,
        last_action, last_action_date, url, pdf_link, txt_link, amendments,
        amendment_links, see_also, history
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (bill_id) DO NOTHING;
"""

#insert bills into database
for bill in bills_data:
    try:
        doc_type = bill.get("docType", "UNKNOWN")
        bill_id = str(bill.get("billId") or bill.get("bill_id"))
        bill_number = bill.get("billNumber") or bill.get("bill_number")
        session = bill.get("session", "UNKNOWN")
        title = bill.get("title") or "UNKNOWN"
        description = bill.get("description", "UNKNOWN")
        status = bill.get("status", "UNKNOWN")
        status_date = bill.get("statusDate")
        last_action = bill.get("last_action", "UNKNOWN")
        last_action_date = bill.get("last_action_date")
        url = bill.get("url", "UNKNOWN")
        pdf_link = bill["links"].get("pdf", "N/A") if "links" in bill else "N/A"
        txt_link = bill["links"].get("txt", "N/A") if "links" in bill else "N/A"

        #convert list fields to a readable string format
        amendments = "; ".join([amend.get("title", "N/A") for amend in bill.get("amendments", [])])
        amendment_links = "; ".join([amendment.get("pdf", "N/A") for amendment in bill.get("amendment_links", [])])
        see_also = "; ".join([related.get("sast_bill_number", "N/A") for related in bill.get("seeAlso", [])])
        history = "; ".join([f"{hist.get('date', 'N/A')} - {hist.get('action', 'N/A')}" for hist in bill.get("history", [])])

        #convert date fields
        if status_date:
            try:
                status_date = datetime.strptime(status_date, "%Y-%m-%d")
            except ValueError:
                print(f"Invalid date format: {status_date}")
                status_date = None

        if last_action_date:
            try:
                last_action_date = datetime.strptime(last_action_date, "%Y-%m-%d")
            except ValueError:
                print(f"Invalid date format: {last_action_date}")
                last_action_date = None

        #ensure required fields are present
        if not bill_number or not bill_id or not title:
            print(f"Skipping bill due to missing required fields: {bill}")
            continue

        #insert data into database
        cur.execute(insert_query, (
            doc_type, bill_id, bill_number, session, title, description, status, status_date,
            last_action, last_action_date, url, pdf_link, txt_link, amendments,
            amendment_links, see_also, history
        ))
        conn.commit()
        print(f"Inserted bill {bill_number} ({bill_id})")

    except Exception as e:
        print(f"Error inserting bill {bill_number}: {e}")
        print(f"Query data: {bill_number}, {bill_id}, {status_date}, {status}, {title}, {description}")
        conn.rollback()

#close connections
cur.close()
conn.close()
print("Data successfully inserted into Supabase")

