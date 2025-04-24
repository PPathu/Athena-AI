import os
import psycopg2
import psycopg2.extras
import concurrent.futures
import google.generativeai as genai
from google.api_core.client_options import ClientOptions
from google.api_core.exceptions import ResourceExhausted
from dotenv import load_dotenv, find_dotenv
from supabase import create_client

#load env variables
load_dotenv(find_dotenv())
DATABASE_URL   = os.getenv("DATABASE_URL")
SUPABASE_URL   = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_KEY   = os.getenv("REACT_APP_SUPABASE_ANON_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not (DATABASE_URL and SUPABASE_URL and SUPABASE_KEY and GEMINI_API_KEY):
    raise SystemExit("Missing one of DATABASE_URL, SUPABASE_URL, SUPABASE_KEY or GEMINI_API_KEY in .env")

#create Supabase client for reading which rows need processing
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
print("Supabase connected")

genai.configure(
    api_key        = GEMINI_API_KEY,
)
model = genai.GenerativeModel("gemini-1.5-pro")
print("Gemini paid endpoint configured")

def fetch_bill_details(bill_id, pg_conn):
    """Retrieve bill data from enhanceddata table by bill_id."""
    with pg_conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
        cur.execute("""
            SELECT title, description, status, status_date,
                   last_action, last_action_date, url
              FROM enhanceddata
             WHERE bill_id = %s
        """, (bill_id,))
        row = cur.fetchone()
    if not row:
        # fallback if the bill record is missing
        return ("Unknown Title", "No description available",
                "Unknown Status", None,
                "Unknown Last Action", None,
                "No URL")
    return row

def make_prompt(bill):
    """Construct the 1–2 sentence summarization prompt."""
    title, desc, status, sdate, action, adate, url = bill
    return (
        "You are an expert in legislative analysis and plain language translation.\n"
        "Provide a 1–2 sentence summary that conveys the key purpose and impact.\n"
        "Avoid any legislative jargon. If essential info is missing, respond with only the URL\n"
        "or 'not enough bill information at the moment'.\n\n"
        f"Bill Info:\n"
        f" Title: {title or 'N/A'}\n"
        f" Description: {desc or 'N/A'}\n"
        f" Status: {status or 'N/A'} (as of {sdate or 'N/A'})\n"
        f" Last Action: {action or 'N/A'} on {adate or 'N/A'}\n"
        f" URL: {url or 'N/A'}\n\n"
    )

def insert_summary(record_id, prompt, text, pg_conn):
    """Write the AI summary back into ai_summaries_enhanced by id."""
    with pg_conn.cursor() as cur:
        cur.execute("""
            UPDATE ai_summaries_enhanced
               SET desc_prompt   = %s,
                   desc_response = %s
             WHERE id = %s
        """, (prompt, text, record_id))
    pg_conn.commit()

def work_bill(rec):
    """
    Worker function: given a dict with 'id' and 'bill_id',
    fetch details, call Gemini
    """
    rec_id  = rec["id"]
    bill_id = rec["bill_id"]
    pg_conn = psycopg2.connect(DATABASE_URL)

    try:
        bill   = fetch_bill_details(bill_id, pg_conn)
        prompt = make_prompt(bill)

        print(f"[Rec {rec_id} | Bill {bill_id}] Calling Gemini")
        try:
            resp = model.generate_content(prompt)
            text = resp.text if resp and resp.text else None
        except ResourceExhausted:
            print(f"[Rec {rec_id}] Rate limited by Gemini, skipping")
            return
        except Exception as e:
            print(f"[Rec {rec_id}] Gemini error: {e}")
            return

        if text:
            insert_summary(rec_id, prompt, text, pg_conn)
            print(f"[Rec {rec_id}] Summary stored")
        else:
            print(f"[Rec {rec_id}] Empty response, no update")

    finally:
        pg_conn.close()


def main():
    # select all rows that still need a desc_response
    rows = (
        supabase
          .table("ai_summaries_enhanced")
          .select("id, bill_id")
          .is_("desc_response", None)
          .execute()
          .data
    ) or []
    print(f"{len(rows)} records to process")

    # process in parallel with threadpool
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(work_bill, rows)

    print("Done!!!")

if __name__ == "__main__":
    main()
