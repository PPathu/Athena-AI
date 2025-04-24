import os
import psycopg2
import psycopg2.extras
import google.generativeai as genai
from datetime import datetime, timezone
from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client
from google.api_core.exceptions import ResourceExhausted
import time
from psycopg2 import OperationalError

conn = None
cur = None
supabase = None
model = None 

def generate_content_with_retry(prompt, mode):
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            resp = model.generate_content(prompt)
            if resp and resp.text:
                return resp.text
            print(f"[{mode}] empty response")
            return None
        except ResourceExhausted as e:
            backoff = 5
            print(f"[{mode}] rate limit (429), sleeping {backoff}s (attempt {attempt}) ")
            time.sleep(backoff)
        except Exception as e:
            print(f"[{mode}] unexpected error: {e}")
            return None
    print(f"[{mode}] failed after {max_retries} retries")
    return None


def connectSupabase():
    """
    Establish database connection (PostgreSQL) and create a Supabase client.
    """
    global conn, cur, supabase
    
    dotenv_path = find_dotenv()
    if not load_dotenv(dotenv_path):
        print("Error: .env file not loaded")
        exit()

    DATABASE_URL = os.getenv("DATABASE_URL")
    SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
    SUPABASE_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Error: Missing REACT_APP_SUPABASE_URL or REACT_APP_SUPABASE_ANON_KEY in .env")
        exit()

    try:
        # connect with psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # initialize Supabase client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connection established")
    except Exception as e:
        print(f"Supabase connection failed: {e}")

def disconnectSupabase():
    """Close database connection."""
    global cur, conn
    try:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("Supabase disconnected")
    except Exception as e:
        print(f"Supabase disconnection failed: {e}")


def store_ai_summary(bill_id, mode, txt):
    """
    Updates the ai_summaries_enhanced table, setting the appropriate column
    for the chosen mode to the AI-generated text.
    """
    column_map = {
        "simple": "response_simple",
        "intermediate": "response_intermediate",
        "persuasive": "response_persuasive",
        "pros_cons": "response_pros_cons",
        "tweet": "response_tweet"
    }
    column_name = column_map.get(mode)

    if not column_name:
        print(f"Unknown mode '{mode}'. Not storing summary.")
        return

    update_query = f"""
        UPDATE ai_summaries_enhanced
        SET {column_name} = %s
        WHERE bill_id = %s
    """

    try:
        cur.execute(update_query, (txt, bill_id))
        conn.commit()
        print(f"[{mode}] AI summary stored for Bill ID {bill_id}.")
    except Exception as e:
        print(f"Failed to store AI summary for Bill {bill_id}, mode '{mode}': {e}")
        conn.rollback()


def fetchBillDetails(bill_id):
    query = """
        SELECT title, description, status, status_date, last_action, last_action_date, url
        FROM enhanceddata 
        WHERE bill_id = %s
    """
    try:
        cur.execute(query, (bill_id,))
    except OperationalError as e:
        print("DB connection lost. Reconnecting...")
        connectSupabase() 
        cur.execute(query, (bill_id,))
    bill = cur.fetchone()
    if not bill:
        print(f"No bill found for Bill ID {bill_id} in enhanceddata.")
        return ("Unknown Title", "No description available", "Unknown Status", None, 
                "Unknown Last Action", None, "No URL")
    return bill


def create_prompt_simple(bill):
    """
    Very basic, plain-language summary. Explains the bill as if to a newcomer.
    """
    title, description, status, status_date, last_action, last_action_date, url = bill
    title = title or "Unknown Title"
    description = description or "No description available"
    status = status or "Unknown Status"
    status_date = status_date or "N/A"
    last_action = last_action or "Unknown Last Action"
    last_action_date = last_action_date or "N/A"
    url = url or "No URL"

    return (
        "You are an expert in legislative analysis and plain language translation.\n"
        "Your task is to simplify and summarize legislative bills in a clear, concise, "
        "and accessible way for the general public.\n"
        "Use very basic language, as if explaining to a newcomer.\n\n"
        "Maintain factual accuracy.\n"
        "No italic, bold, or underlined text.\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Status: {status} (as of {status_date})\n"
        f"Last Action: {last_action} (on {last_action_date})\n"
        f"URL: {url}\n"
    )

def create_prompt_intermediate(bill):
    """
    More detailed summary than 'simple', but still avoiding heavy legal jargon.
    Good for a general audience wanting moderate detail.
    """
    title, description, status, status_date, last_action, last_action_date, url = bill
    title = title or "Unknown Title"
    description = description or "No description available"
    status = status or "Unknown Status"
    status_date = status_date or "N/A"
    last_action = last_action or "Unknown Last Action"
    last_action_date = last_action_date or "N/A"
    url = url or "No URL"

    return (
        "You are an expert in legislative analysis and plain language translation.\n"
        "Please summarize this bill for a general audience that wants moderate detail.\n"
        "Explain what the bill does, why it matters, and any potential impact.\n\n"
        "Ensure factual accuracy.\n"
        "No italic, bold, or underlined text.\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Status: {status} (as of {status_date})\n"
        f"Last Action: {last_action} (on {last_action_date})\n"
        f"URL: {url}\n"
    )

def create_prompt_persuasive(bill):
    """
    A 'why should you care' approach, focusing on persuading or showing the bill's importance.
    """
    title, description, status, status_date, last_action, last_action_date, url = bill
    title = title or "Unknown Title"
    description = description or "No description available"
    status = status or "Unknown Status"
    status_date = status_date or "N/A"
    last_action = last_action or "Unknown Last Action"
    last_action_date = last_action_date or "N/A"
    url = url or "No URL"

    return (
        "You are an expert in legislative analysis and plain language translation.\n"
        "Please summarize this bill in a persuasive manner, focusing on why someone should care.\n"
        "Highlight positive impact or benefits.\n\n"
        "Maintain factual accuracy.\n"
        "No italic, bold, or underlined text.\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Status: {status} (as of {status_date})\n"
        f"Last Action: {last_action} (on {last_action_date})\n"
        f"URL: {url}\n"
    )

def create_prompt_pros_cons(bill):
    """
    Lists potential pros and cons, plus a neutral summary of its purpose.
    """
    title, description, status, status_date, last_action, last_action_date, url = bill
    title = title or "Unknown Title"
    description = description or "No description available"
    status = status or "Unknown Status"
    status_date = status_date or "N/A"
    last_action = last_action or "Unknown Last Action"
    last_action_date = last_action_date or "N/A"
    url = url or "No URL"

    return (
        "You are an expert in legislative analysis and plain language translation.\n"
        "Provide a balanced summary of this bill, including potential pros and cons.\n\n"
        "Maintain factual accuracy.\n"
        "No italic, bold, or underlined text.\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Status: {status} (as of {status_date})\n"
        f"Last Action: {last_action} (on {last_action_date})\n"
        f"URL: {url}\n"
    )

def create_prompt_tweet_sized(bill):
    """
    Generates a tweet-sized (280 characters or less) summary of a bill.
    """
    title, description, status, status_date, last_action, last_action_date, url = bill
    title = title or "Unknown Title"
    description = description or "No description available"
    status = status or "Unknown Status"
    status_date = status_date or "N/A"
    last_action = last_action or "Unknown Last Action"
    last_action_date = last_action_date or "N/A"
    url = url or "No URL"

    return (
        "Summarize this bill in 280 characters or less for a general audience.\n"
        "Keep it factual, clear, and engaging. No bold/italic text.\n\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Status: {status} (as of {status_date})\n"
        f"Last Action: {last_action} (on {last_action_date})\n"
        f"URL: {url}\n"
        "Keep it short & tweet-friendly!"
    )


def generate_ai_summary_for_mode(bill_id, mode):
    """
    Generate a summary for a given bill_id and mode (simple, intermediate, 
    persuasive, pros_cons, tweet), then store in the DB.
    """
    # fetch details
    bill_details = fetchBillDetails(bill_id)

    # pick the prompt
    if mode == "simple":
        prompt = create_prompt_simple(bill_details)
    elif mode == "intermediate":
        prompt = create_prompt_intermediate(bill_details)
    elif mode == "persuasive":
        prompt = create_prompt_persuasive(bill_details)
    elif mode == "pros_cons":
        prompt = create_prompt_pros_cons(bill_details)
    elif mode == "tweet":
        prompt = create_prompt_tweet_sized(bill_details)
    else:
        print(f"Mode '{mode}' not recognized. Skipping.")
        return

    content = generate_content_with_retry(model, prompt, mode)
    if content:
        store_ai_summary(bill_id, mode, content)
    else:
        print(f"Failed to get content for Bill ID {bill_id}, mode {mode}")

if __name__ == "__main__":
    
    load_dotenv(find_dotenv())
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro")
    print("Connected to Gemini")

    connectSupabase()

    # 3) batch + back-off settings
    BATCH_SIZE     = 1
    SLEEP_BETWEEN  = 5    # secs between bills
    GLOBAL_BACKOFF = 300   # secs on global quota hit
    fail_counts    = {}

    while True:
        resp = supabase.table("ai_summaries_enhanced") \
            .select(
                "bill_id, response_simple, response_intermediate, "
                "response_persuasive, response_pros_cons, response_tweet"
            ) \
            .or_(
                "response_simple.is.null,"
                "response_intermediate.is.null,"
                "response_persuasive.is.null,"
                "response_pros_cons.is.null,"
                "response_tweet.is.null"
            ) \
            .limit(BATCH_SIZE) \
            .execute()

        rows = resp.data or []
        if not rows:
            print("All done—no bills left.")
            break

        row   = rows[0]
        bill  = row["bill_id"]
        print(f"Generating for Bill {bill}")

        try:
            for mode, col in [
                ("simple",       "response_simple"),
                ("intermediate", "response_intermediate"),
                ("persuasive",   "response_persuasive"),
                ("pros_cons",    "response_pros_cons"),
                ("tweet",        "response_tweet"),
            ]:
                if row[col] is not None:
                    continue

                prompt = {
                    "simple":       create_prompt_simple,
                    "intermediate": create_prompt_intermediate,
                    "persuasive":   create_prompt_persuasive,
                    "pros_cons":    create_prompt_pros_cons,
                    "tweet":        create_prompt_tweet_sized,
                }[mode](fetchBillDetails(bill))

                text = generate_content_with_retry(prompt, mode)
                if text:
                    store_ai_summary(bill, mode, text)

            print(f"⏸ Sleeping {SLEEP_BETWEEN}s…")
            time.sleep(SLEEP_BETWEEN)

        except ResourceExhausted:
            fail_counts[bill] = fail_counts.get(bill, 0) + 1
            if fail_counts[bill] >= 2:
                print(f"Bill {bill} failed twice—skipping modes")
                for mode, col in [
                    ("simple",       "response_simple"),
                    ("intermediate", "response_intermediate"),
                    ("persuasive",   "response_persuasive"),
                    ("pros_cons",    "response_pros_cons"),
                    ("tweet",        "response_tweet"),
                ]:
                    if row[col] is None:
                        store_ai_summary(bill, mode, "[skipped—quota]")
            else:
                print(f"Global quota hit—sleeping {GLOBAL_BACKOFF}s…")
                time.sleep(GLOBAL_BACKOFF)

    disconnectSupabase()