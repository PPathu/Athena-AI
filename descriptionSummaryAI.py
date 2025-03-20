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

def insertDescSummaryAI(billID, prompt, response):
    try:
        # ToDo: Modify this: Maybe add col in enhanceddata and make it so it finds the corrisponding bill id and inserts the summary into that col
        update_query = """
            UPDATE ai_summaries_enhanced
            SET desc_response = %s, desc_prompt = %s
            WHERE bill_id = %s
        """
        cur.execute(update_query, (response, prompt, billID))
        conn.commit()
        print(f"Short description AI summary inserted for Bill ID {billID}")

    except Exception as e:
        print(f"failed to insert AI summary: {e}")

def fetchBillDetails(billID):
    """Retrieve bill details from `enhanceddata` for AI summarization"""
    query = """
        SELECT title, description, status, status_date, last_action, last_action_date, url
        FROM enhanceddata WHERE bill_id = %s
    """
    cur.execute(query, (billID,))
    bill = cur.fetchone()

    if not bill:
        print(f"no bill found for Bill ID {billID} in enhanceddata - proceeding with minimal data")
        return ("Unknown Title", "No description available", "Unknown Status", None, "Unknown Last Action", None, "No URL")

    return bill

def createPromptV2(bill):
    title, description, status, status_date, last_action, last_action_date, url = bill

    #ensure no field is None
    title = title or "Unknown Title"
    description = description or "No description available"
    status = status or "Unknown Status"
    status_date = status_date or "N/A"
    last_action = last_action or "Unknown Last Action"
    last_action_date = last_action_date or "N/A"
    url = url or "No URL" 

    # Modfied the prompt to ask for 1-2 sentance summary
    prompt = (
        "You are an expert in legislative analysis and plain language translation.\n"
        "Your task is to simplify and summarize legislative bills in a clear, concise, and accessible way for the general public.\n"
        "Provide a 1-2 sentence summary of the bill that conveys the key purpose and impact in plain language.\n"
        "Avoid using any technical legislative terms or jargon.\n"
        "If any key information is missing, provide only the URL or 'not enough bill information at the moment' if there is no URL.\n\n"
        f"Here is the Bill Information:\n"
        f"Title: {title}\n"
        f"Description: {description}\n"
        f"Status: {status} (as of {status_date})\n"
        f"Last Action: {last_action} (on {last_action_date})\n"
        f"URL: {url}\n\n"
    )
    return prompt

def generateAiSummary(billID):
    """Fetch bill details, generate summary using AI, and store result"""
    dotenv_path = find_dotenv()
    if not load_dotenv(dotenv_path):
        print("Error: .env file not loaded")
        exit()

    #load Gemini API key
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY not found in .env file")
        exit()
    
    #configure Gemini API
    try:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-pro")  # TODO: Decide on model
        print("Successfully connected to Gemini API")
    except Exception as e:
        print(f"Failed to connect to Gemini: {e}")
        exit()
    
    #get bill details
    bill = fetchBillDetails(billID)

    #generate prompt
    #prompt = createPromptV1(bill)
    prompt = createPromptV2(bill)

    #call Gemini API
    try:
        response = model.generate_content(prompt)
        if response and response.text:
            timestamp = datetime.now(timezone.utc)
            insertDescSummaryAI(billID, prompt, response.text)
        else:
            print(f"Gemini response was empty for Bill ID {billID}")
    except Exception as e:
        print(f"failed to get response from Gemini: {e}")

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


if __name__ == "__main__":
    connectSupabase()
    
    #generate AI summary for a sample bill
    response = supabase.table("bills").select("*").execute()
    if response.data:
        print("responses exist")
        for bill in response.data:
            billID = bill.get("billid")
            print(billID)
            if billID:
                print("billID exists")
                generateAiSummary(billID)
                print("generated billID {billID}")
                
    # to run on single bill instead of all billId
    # if billID is not None and int(billID) == 1968867:
    
    #bill_id_to_summarize = "1968867"
    #generateAiSummary(bill_id_to_summarize)

    disconnectSupabase()
