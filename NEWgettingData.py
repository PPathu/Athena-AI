from dotenv import load_dotenv
from keys import legiscanKey
import requests
import json
import base64
import PyPDF2
import os
import csv

#constants
csv_file_name = "NEWbills_data.csv"
STATE = "WI"

def directory_exists():
    os.makedirs('Bill Text', exist_ok=True)

def find_doc_type(bill_number: str) -> str:
    bill_number = bill_number.upper()
    if bill_number.startswith("AB"):
        return "Assembly Bill"
    elif bill_number.startswith("SB"):  
        return "Senate Bill"
    elif bill_number.startswith("AJR"):
        return "Assembly Joint Resolution"
    elif bill_number.startswith("SJR"):
        return "Senate Joint Resolution"
    elif bill_number.startswith("AR"):
        return "Assembly Resolution"
    elif bill_number.startswith("SR"):
        return "Senate Resolution"
    else:
        return "Unknown"

def map_status_code(status_code: int) -> str:
    mapping = {
        1: "Introduced",
        2: "Engrossed",
        3: "Enrolled",
        4: "Signed",
        5: "Vetoed",
        6: "Failed"
    }
    return mapping.get(status_code, f"Status: {status_code}")


def get_session_info():
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getSessionList&state=WI"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error: Failed to fetch session list")
        return "UNKNOWN SESSION"
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response")
        return "UNKNOWN SESSION"

    if "sessions" in data and isinstance(data["sessions"], list):
        latest_session = max(data["sessions"], key=lambda x: x["year_start"])  # Get the newest session by year
        return latest_session.get("session_name", "UNKNOWN SESSION")
    return "UNKNOWN SESSION"



#1. get the master list for current session
#2. for each bill, get docId 
#3. download pdf, extract text
#4. build json structure in new format and save it to newFormatData.json
def get_master_list():
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getMasterList&id=2197"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error: Failed to fetch master list")
        print("Status Code:", response.status_code)
        return []
    try:
        data = response.json()
    except json.JSONDecodeError:
        print("Error: Failed to parse JSON response.")
        return []

    session_info = get_session_info()

    bills = []
    for key, bill in data["masterlist"].items():
        if key == "session":
            continue

        bill_id = bill.get("bill_id")
        bill_number = bill.get("number", "UNKNOWN")
        doc_id = get_doc_id(bill_id) if bill_id else None

        if doc_id:
            get_bill_text(doc_id)

        bill_details = fetch_bill_details(bill_id) if bill_id else {}

        new_bill_data = {
            "docType": find_doc_type(bill_number),
            "billNumber": bill_number,
            "session": session_info,
            "title": bill.get("title", "UNKNOWN"),
            "description": bill.get("description", "UNKNOWN"),
            "status": map_status_code(bill.get("status", 0)),
            "statusDate": bill.get("status_date", "UNKNOWN"),
            "last_action": bill.get("last_action", "UNKNOWN"),
            "last_action_date": bill.get("last_action_date", "UNKNOWN"),
            "url": bill.get("url", "UNKNOWN"),
            "links": {
                "pdf": f"Bill Text/bill_{doc_id}.pdf" if doc_id else None,
                "txt": f"Bill Text/bill_{doc_id}.txt" if doc_id else None
            },
            "amendments": bill_details.get("amendments", []),
            "seeAlso": bill_details.get("seeAlso", []),
            "history": bill_details.get("history", [])
        }

        #debugging statements
        print(f"Processed Bill: {bill_number}")
        print(f"Session: {new_bill_data['session']}")
        print(f"Amendments: {len(new_bill_data['amendments'])} items")
        print(f"See Also: {len(new_bill_data['seeAlso'])} items")
        print(f"History: {len(new_bill_data['history'])} items\n")

        bills.append(new_bill_data)

    output_file = "NEWdata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=4)

    print(f"JSON data saved to {output_file}")
    save_to_csv(bills)
    return bills


def get_doc_id(bill_id):
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getBill&id={bill_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'bill' in data:
            bill_data = data['bill']
            texts = bill_data.get('texts', [])
            if texts and 'doc_id' in texts[0]:
                doc_id = texts[0]['doc_id']
                print(f"Found doc_id={doc_id} for bill_id={bill_id}")
                return doc_id
    print(f"Bill doc_id not found for bill_id={bill_id}")
    return None


def get_bill_text(doc_id):
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getBillText&id={doc_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        text_data = data.get('text')
        if text_data and 'doc' in text_data:
            doc_base64 = text_data['doc']
            try:
                decoded_doc = base64.b64decode(doc_base64)
                directory_exists()

                #save pdf
                pdf_file = f"Bill Text/bill_{doc_id}.pdf"
                with open(pdf_file, 'wb') as f:
                    f.write(decoded_doc)
                print(f"Saved bill text to {pdf_file}")

                #extract text from pdf
                with open(pdf_file, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        pdf_text += page.extract_text() or ""
                
                #save extracted text
                txt_file = f"Bill Text/bill_{doc_id}.txt"
                with open(txt_file, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(pdf_text)
                print(f"Text extracted and saved as {txt_file}")
            
            except Exception as e:
                print(f"Error decoding or saving docuemnt for doc_id={doc_id}: {e}")
        else:
            print(f"No 'doc' found in text data for doc_id={doc_id}")
    else:
        print(f"Issue getting text data for doc_id={doc_id}")

#gets the bill details, including amendments, related bills (sasts), and history
def fetch_bill_details(bill_id):
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getBill&id={bill_id}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Failed to fetch bill details for Bill ID {bill_id}")
        return {}
    try:
        data = response.json()
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON response for Bill ID {bill_id}")
        return {}

    bill_data = data.get("bill", {})

    print(f"   sasts (related bills): {len(bill_data.get('sasts', []))}")

    return {
        "amendments": bill_data.get("amendments", []),
        "seeAlso": bill_data.get("sasts", []),
        "history": bill_data.get("history", [])
    }

#saves extracted bill data to CSV file & converts list fields into strings
def save_to_csv(bills):
    output_file = "NEWbills_data.csv"

    headers = [
        "docType", "billNumber", "session", "title", "description", 
        "status", "statusDate", "last_action", "last_action_date", "url", 
        "pdf_link", "txt_link", "amendments", "seeAlso", "history"
    ]

    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for bill in bills:
            writer.writerow([
                bill.get("docType", "UNKNOWN"),
                bill.get("billNumber", "UNKNOWN"),
                bill.get("session", "UNKNOWN"),
                bill.get("title", "UNKNOWN"),
                bill.get("description", "UNKNOWN"),
                bill.get("status", "UNKNOWN"),
                bill.get("statusDate", "UNKNOWN"),
                bill.get("last_action", "UNKNOWN"),
                bill.get("last_action_date", "UNKNOWN"),
                bill.get("url", "UNKNOWN"),
                bill["links"].get("pdf", "N/A") if "links" in bill else "N/A",
                bill["links"].get("txt", "N/A") if "links" in bill else "N/A",
                "; ".join([amend.get("title", "N/A") for amend in bill.get("amendments", [])]),  
                "; ".join([related.get("billNumber", "N/A") for related in bill.get("seeAlso", [])]),  
                "; ".join([f"{hist.get('date', 'N/A')} - {hist.get('action', 'N/A')}" for hist in bill.get("history", [])])  
            ])
    print(f"CSV data saved to {output_file}")


if __name__ == "__main__":

    #load api key 
    load_dotenv()
    legiscanKey = os.getenv("LEGISCAN_API_KEY")

    if not legiscanKey:
        print("Error:missing LegiScan API Key - make sure it's in your .env file")
        exit(1)

    directory_exists()
    session_name = get_session_info()

    print(f"Current session: {session_name}")

    bills = get_master_list()

    if not bills:
        print("No bills retrieved. Check API response or session ID")
    else:
        print(f"successfully retrieved {len(bills)} bills")

    output_json = "NEWdata.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=4)
    print(f"JSON data saved to {output_json}")

    save_to_csv(bills)
    print("PROCESS COMPLETED")
