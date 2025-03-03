from dotenv import load_dotenv
import os
import psycopg2
import psycopg2.extras
from google import genai
from datetime import datetime, timezone

conn = None
cur = None




def insertAiSummary(billID, timestamp, llm, prompt, response):
    try:
        insert_query = """
            INSERT INTO aisummary(billid, timestamp, llm, prompt, response)
            VALUES (%s, %s, %s, %s, %s)
        """
        cur.execute(insert_query, (billID, timestamp, llm, prompt, response))
        conn.commit()
    except Exception as e:
        print("Failed insert ai summary into table: {e}")



def geminiSummary(billID):
    #load .env variables
    dotenv_path="../../credential/.env"
    if not load_dotenv(dotenv_path):
        print("ERROR: .env not loaded")
        exit


    # connects to gemini api
    API_KEY = os.getenv("API_KEY")
    try:
        client = genai.Client(api_key=API_KEY)
    except Exception as e:
        print("Failed to connect to gemini: {e}")
        exit   



    # retrieves bill information
    bill= queryBill(billID)

    # created V1 prompt
    prompt= createPromptV1(bill)
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
    except Exception as e:
        print("Failed to get response from gemini: {e}")
        exit


    #insert our results into aiSummary table
    timestamp = datetime.now(timezone.utc)
    insertAiSummary(billID, timestamp , "gemini" , prompt , response.text)



#uses the bills title and description for context
def createPromptV1(bill):
    title= bill['title']
    description= bill['bill_description']
    prompt= (
        "You are an expert in legislative analysis and plain language translation."
        "Your task is to simplify and summarize legislative bills in a clear, concise, and accessible way. "
        "Provide a summary that captures the essence of the bill while maintaining factual accuracy. "
        "Avoid legal jargon and make it understandable to the general public. "
        "Here is the bill information:\n\n"
        "Title: {0}\n"
        "Description: {1}\n\n"
        "### Your Task:\n"
        "- Summarize the bill in simple terms.\n"
        "- Highlight its key purpose and potential impact.\n"
        "- If relevant, mention which topics or policy areas it addresses.\n\n"
        "Provide a clear and well-structured response that enhances civic understanding."
    )


    return prompt.format(title, description)
    



def queryBill(billID):
    query = """
        SELECT * FROM enhanceddata
        WHERE bill_id= %s
    """
    cur.execute(query, (billID,))
    bill = cur.fetchone()
    return bill  



def connectSupabase():
    global conn, cur

    #load .env variables
    dotenv_path="../../credential/.env"
    if not load_dotenv(dotenv_path):
        print("ERROR: .env not loaded")
        exit

    
    DATABASE_URL = os.getenv("DATABASE_URL")
    # Connect to Supabase
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor) 
        print("Supabase connection established")
    except Exception as e:
        print("Supabase connection failed: {e}")


def disconnectSupabase():
    try:
        cur.close()
        conn.close()
        print("Supabase disconnected")
    except Exception as e:
        print("Supabase disconnection failed: {e}")


# temporary/helper function since project structure isnt set in stone yet. Made just in case
def checkDirectoryExists(directory):
    if os.path.exists(directory):
        print("directory exists")
        return True
    else:
        print("directory doesnt exists")
        return False


if __name__ == "__main__":
    #TODO: agree upon project structure, for now doing this as the directory. env checked in connectSupabase() and geminiSummary()
    checkDirectoryExists('../data/BillText')

    connectSupabase()

    #billid of bill that is an act: 1974122, billAB50, BUT, VERY long full bill
    #Temporary: we will use 1968867, because its full description bill is smaller, and when we get to 
    #getting the full description/details of the bill, llm will have no issue reading all the information
    geminiSummary("1968867")

    disconnectSupabase()
    
    