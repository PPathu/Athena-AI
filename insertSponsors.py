import os
import psycopg2
import psycopg2.extras
import google.generativeai as genai
from datetime import datetime, timezone
from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client
import os
from dotenv import load_dotenv, find_dotenv
 
global conn, cur, supabase
conn = None
cur = None
 
import json
def insert_sponsors_from_json(json_path, bill_id_filter=None):
    try:
        with open(json_path, "r") as f:
            bills_data = json.load(f)
 
        # Filter bills based on bill_id_filter if provided
        for bill in bills_data:
            bill_id = bill.get("billId") 
            sponsors = bill.get("sponsors")
 
            if bill_id_filter and bill_id != bill_id_filter:
                print("here")
                continue  
 
            if bill_id and sponsors:
                response = supabase.table("enhanceddata").update({
                    "sponsors": sponsors  
                }).eq("bill_id", bill_id).execute()
            else:
                print(f"Skipping bill_id {bill_id} - missing data")
    except Exception as e:
        print(f"Failed to insert sponsor data: {e}")
 
 
 
 
 
def connectSupabase():
    """Establish database connection"""
    global conn, cur
    dotenv_path = find_dotenv()
    if not load_dotenv(dotenv_path):
        print("Error: .env file not loaded")
        exit()
 
    DATABASE_URL = os.getenv("DATABASE_URL")
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        print("Supabase connection established")
    except Exception as e:
        print(f"Supabase connection failed: {e}")
 
def disconnectSupabase():
    """Close database connection"""
    try:
        cur.close()
        conn.close()
        print("Supabase disconnected")
    except Exception as e:
        print(f"Supabase disconnection failed: {e}")
 
def connectSupabase():
    """Establish database connection and Supabase client"""
    global conn, cur, supabase  # Ensure supabase is a global variable
     
    dotenv_path = find_dotenv()
    if not load_dotenv(dotenv_path):
        print("Error: .env file not loaded")
        exit()
 
    # Load environment variables (Updated to match your .env)
    DATABASE_URL = os.getenv("DATABASE_URL")
    SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")  # Updated
    SUPABASE_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")  # Updated
 
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: REACT_APP_SUPABASE_URL or REACT_APP_SUPABASE_ANON_KEY is missing from the .env file")
        exit()
 
    try:
        # Connect with psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
        # Initialize Supabase client
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
 
        print("Supabase connection established")
    except Exception as e:
        print(f"Supabase connection failed: {e}")
 
import requests  # Add at top if not already imported
 
if __name__ == "__main__":
    connectSupabase()
 
    # Change the bill_id below to the one you want to test
    test_bill_id = 1952554
    insert_sponsors_from_json("Athena-AI/NEWdata.json")
 
    disconnectSupabase()