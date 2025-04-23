from dotenv import load_dotenv
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
        latest_session = max(data["sessions"], key=lambda x: x["year_start"])
        return latest_session.get("session_name", "UNKNOWN SESSION")
    return "UNKNOWN SESSION"


def fetch_bill_details(bill_id):
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getBill&id={bill_id}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: failed to get bill details for Bill ID {bill_id}")
        return {}

    try:
        data = response.json()
    except json.JSONDecodeError:
        print(f"Error: failed to get JSON response for Bill ID {bill_id}")
        return {}

    bill_data = data.get("bill", {})

    sponsors = []
    for sponsor in bill_data.get("sponsors", []):
        sponsors.append({
            "name": sponsor.get("name"),
            "party": sponsor.get("party"),
            "role": sponsor.get("role"),
            "district": sponsor.get("district"),
            "ballotpedia": sponsor.get("ballotpedia"),
            "votesmart_id": sponsor.get("votesmart_id"),
        })
        
    return {
        "amendments": bill_data.get("amendments", []),
        "seeAlso": bill_data.get("sasts", []),
        "history": bill_data.get("history", []),
        "sponsors": sponsors
    }


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
                # print(f"Found doc_id={doc_id} for bill_id={bill_id}")
                return doc_id
    print(f"⚠️ Bill doc_id not found for bill_id={bill_id}")
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

                #save PDF
                pdf_file = f"Bill Text/bill_{doc_id}.pdf"
                with open(pdf_file, 'wb') as f:
                    f.write(decoded_doc)
                print(f"Saved bill text to {pdf_file}")

                #extract text from PDF
                with open(pdf_file, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_text = "".join([page.extract_text() or "" for page in pdf_reader.pages])

                #save extracted text
                txt_file = f"Bill Text/bill_{doc_id}.txt"
                with open(txt_file, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(pdf_text)
                # print(f"Text extracted and saved as {txt_file}")
            
            except Exception as e:
                print(f"Error decoding or saving document for doc_id={doc_id}: {e}")
        else:
            print(f"No 'doc' found in text data for doc_id={doc_id}")
    else:
        print(f"Issue getting text data for doc_id={doc_id}")


def get_master_list():
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getMasterList&id=2197"
    response = requests.get(url)

    if response.status_code != 200:
        print("Error: Failed to fetch master list")
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
            "billId": bill_id,
            "billNumber": bill_number,
            "session": session_info,
            "title": bill.get("title") or "No Title Available",
            "description": bill.get("description") or "No Description Available",
            "status": map_status_code(bill.get("status", 0)),
            "statusDate": bill.get("status_date", None),
            "last_action": bill.get("last_action") or "No Last Action Available",
            "last_action_date": bill.get("last_action_date", None),
            "url": bill.get("url") or "No URL Available",
            "amendments": bill_details.get("amendments", []),
            "seeAlso": bill_details.get("seeAlso", []),
            "history": bill_details.get("history", []),
            "sponsors": bill_details.get("sponsors", [])
        }

        # print(f"Retrieved Bill: {new_bill_data['billNumber']} - {new_bill_data['title']}")
        bills.append(new_bill_data)

    output_file = "NEWdata.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=4)

    print(f"JSON data saved to {output_file}")
    return bills


if __name__ == "__main__":
    load_dotenv()
    legiscanKey = os.getenv("LEGISCAN_API_KEY")

    if not legiscanKey:
        print("Error: Missing LegiScan API Key - make sure it's in your .env file.")
        exit(1)

    directory_exists()
    session_name = get_session_info()

    print(f"Current session: {session_name}")

    bills = get_master_list()

    if not bills:
        print("No bills retrieved. Check API response or session ID.")
    else:
        print(f"Successfully retrieved {len(bills)} bills.")

    output_json = "NEWdata.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(bills, f, indent=4)
    print(f"JSON data saved to {output_json}")

    print("PROCESS COMPLETED")
