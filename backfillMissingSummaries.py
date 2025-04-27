import os
import time
import psycopg2
from dotenv import load_dotenv, find_dotenv
import google.generativeai as genai

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

def connectSupabase():
    global conn, cur
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        print("PostgreSQL connected")
    except Exception as e:
        print(f"PostgreSQL connection failed: {e}")

def disconnectSupabase():
    global cur, conn
    try:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL disconnected")
    except Exception as e:
        print(f"Disconnection failed: {e}")


missing_ids = [
    "1979237", "1979260", "1979285", "1979310", "1979335", "1979359", "1979387", "1979412",
    "1979438", "1979463", "1979488", "1979513", "1979544", "1979569", "1979594", "1979619",
    "1979645", "1979670", "1979697", "1979722", "1979747", "1979772", "1979797", "1981130",
    "1981720", "1981731", "1981742", "1981754", "1981766", "1981779", "1981790", "1981803",
    "1981816", "1981827", "1981841", "1981854", "1981865", "1981878", "1981891", "1981904",
    "1981915", "1981928", "1981940", "1981952", "1981965", "1981977", "1981989", "1982000",
    "1984418", "1984480", "1984549", "1984615", "1984683", "1984748", "1984818", "1984886",
    "1984955", "1985024", "1985090", "1985160", "1985228", "1985296", "1985364", "1985433",
    "1988072", "1988277", "1988492", "1988513", "1988535", "1988557", "1988580", "1988604",
    "1988628", "1988652", "1988677", "1988700", "1988724", "1988746", "1988770", "1988794",
    "1988818", "1988843", "1988866", "1988890", "1988913", "1988936", "1988958", "1988982",
    "1989594", "1989693", "1989796", "1989896", "1989998", "1990954", "1992971", "1993176",
    "1993256", "1993337", "1993416", "1993492", "1994778", "1994791", "1994804", "1994816",
    "1994829", "1994843", "1994856", "1994868", "1994881", "1994895", "1994909", "1994922",
    "1994935", "1994948", "1994960", "1994974", "1994987", "1994999", "1995014", "1995027",
    "1995040", "1995054", "1995065", "1995078", "1995091", "1995104", "1995117", "1995131",
    "1995144", "1995156", "1995168", "1995181", "1995194", "1995206", "1995218", "1995231",
    "1995243", "1996606", "2000053", "2000059", "2000065", "2000073", "2000078", "2000086",
    "2000094", "2000101", "2000107", "2000115", "2000125", "2000133", "2000139", "2000145",
    "2000152", "2000158", "2000166", "2000173", "2000180", "2000186", "2000194", "2000204",
    "2000212", "2000217", "2000223", "2000231", "2000239", "2000244", "2000251", "2000257",
    "2005598", "2006600", "2006640", "2006672", "2006710", "2006749", "2006787", "2006828",
    "2006866", "2006906", "2006944", "2007625", "2007661", "2007696", "2007732", "2007768",
    "2007805", "2007842", "2007877", "2007914", "2007951", "2007987", "2008023", "2008059",
    "2008095", "2008133", "2008168", "2008205", "2008241", "2008276"
]

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

    content = generate_content_with_retry(prompt, mode)
    if content:
        store_ai_summary(bill_id, mode, content)
    else:
        print(f"Failed to get content for Bill ID {bill_id}, mode {mode}")

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


if __name__ == "__main__":
    load_dotenv(find_dotenv())
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-pro")
    print("Connected to Gemini")

    connectSupabase()

    for bill_id in missing_ids:
        print(f"Processing Bill ID: {bill_id}")

        for mode in ["simple", "intermediate", "persuasive", "pros_cons", "tweet"]:
            try:
                generate_ai_summary_for_mode(bill_id, mode)
                time.sleep(5)  # avoid Gemini rate limits
            except Exception as e:
                print(f"[ERROR] Bill {bill_id} mode {mode}: {e}")
                continue

        # Now also generate the description summary
        try:
            bill_details = fetchBillDetails(bill_id)
            prompt = (
                "You are an expert in legislative analysis and plain language translation.\n"
                "Provide a 1–2 sentence summary that conveys the key purpose and impact.\n"
                "Avoid any legislative jargon. If essential info is missing, respond with only the URL\n"
                "or 'not enough bill information at the moment'.\n\n"
                f"Bill Info:\n"
                f" Title: {bill_details[0] or 'N/A'}\n"
                f" Description: {bill_details[1] or 'N/A'}\n"
                f" Status: {bill_details[2] or 'N/A'} (as of {bill_details[3] or 'N/A'})\n"
                f" Last Action: {bill_details[4] or 'N/A'} on {bill_details[5] or 'N/A'}\n"
                f" URL: {bill_details[6] or 'N/A'}\n\n"
            )
            text = generate_content_with_retry(prompt, "desc")
            if text:
                cur.execute(
                    "UPDATE ai_summaries_enhanced SET desc_prompt = %s, desc_response = %s WHERE bill_id = %s",
                    (prompt, text, bill_id)
                )
                conn.commit()
                print(f"[desc] Summary stored for Bill ID {bill_id}")
        except Exception as e:
            print(f"[desc] Failed for Bill {bill_id}: {e}")

    disconnectSupabase()
