import requests
from keys import legiscanKey
import json
import base64 
import PyPDF2
import os

STATE = "WI"

# Ensures directories exist for saving files
def ensure_directories():
    os.makedirs('Athena-AI/Bill Text', exist_ok=True)

# Gets ID for every session
def getSessionList():
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getSessionList&state={STATE}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'sessions' in data:
            print("\n Available Wisconsin Legislative Sessions:")
            for session in sorted(data['sessions'], key=lambda x: x['year_start'], reverse=True):
                print(f"- {session['name']} (ID: {session['session_id']})")
            return
    print("\n ERROR: Failed to fetch session list.")

# Gets all the bill IDs from WIS
# Only doing 2025 session
def getMasterList():
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getMasterList&id={2197}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'masterlist' in data:
            print("\n Available Wisconsin Bills:")
            bills = sorted(data['masterlist'].values(), key=lambda x: x.get('status_date', ''), reverse=True)
            billList = []
            for bill in bills:
                billId = bill.get('bill_id', 'UNKNOWN')
                if billId != 'UNKNOWN':
                    docId = getDocId(billId)
                    if docId:
                        getBillText(docId)
                    billData = {
                        "billNumber": bill.get('number', 'UNKNOWN'),
                        "billId": bill.get('bill_id', 'UNKNOWN'),
                        "billStatusDate": bill.get('status_date', 'UNKNOWN'),
                        "billStatus": bill.get('status', 'UNKNOWN'),
                        "billTitle": bill.get('title', 'UNKNOWN'),
                        "billDescription": bill.get('description', 'UNKNOWN'),
                        "pdfFileName": f"bill_{docId}.pdf",
                        "txtFileName": f"bill_{docId}.txt"
                    }
                    billList.append(billData)
            outputFile = 'Athena-AI/data.json'
            with open(outputFile, "w", encoding="utf-8") as f:
                json.dump(billList, f, indent=4)
                
            print(f"Bill data saved to {outputFile}")
            return billList
    print("\n ERROR: Failed to fetch master list.")
    return []

def getDocId(billId):
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getBill&id={billId}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'bill' in data:
            billData = data['bill']
            if 'texts' in billData:
                textData = billData['texts']
                if isinstance(textData, list) and len(textData) > 0 and 'doc_id' in textData[0]:
                    docId = textData[0]['doc_id']
                    print(docId)
                    return docId
    print("\n Bill doc id not found")
    return None

def getBillText(docId):
    url = f"https://api.legiscan.com/?key={legiscanKey}&op=getBillText&id={docId}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if 'text' in data:
            textData = data['text']
            doc = textData['doc']
            try:
                decoded_doc = base64.b64decode(doc)
                # Ensure directory exists
                ensure_directories()

                # Save the decoded content to a file (e.g., as a PDF)
                pdfFileName = f"Athena-AI/Bill Text/bill_{docId}.pdf"
                with open(pdfFileName, 'wb') as f:
                    f.write(decoded_doc)
                print(f"Document saved as {pdfFileName}")
                
                # Now extract text from the saved PDF
                with open(pdfFileName, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    pdf_text = ""
                    for page_num in range(len(pdf_reader.pages)):
                        page = pdf_reader.pages[page_num]
                        pdf_text += page.extract_text()

                # Save the extracted text to a text file with UTF-8 encoding
                txtFileName = f"Athena-AI/Bill Text/bill_{docId}.txt"
                with open(txtFileName, 'w', encoding='utf-8') as txt_file:
                    txt_file.write(pdf_text)
                print(f"Text extracted and saved as {txtFileName}")
            except Exception as e:
                print(f"Error decoding or saving document: {e}")
    else:
        print("\n Issue getting text data from bill")
    return

  
def emptyBillTextFolder(folderPath="Athena-AI/Bill Text"):
    # Check if folder exists
    if os.path.exists(folderPath):
        # List all files in the directory
        files = os.listdir(folderPath)
        for file in files:
            filePath = os.path.join(folderPath, file)
            try:
                # Check if it's a file, not a directory
                if os.path.isfile(filePath):
                    os.remove(filePath)  # Delete the file
                    print(f"Deleted: {filePath}")
            except Exception as e:
                print(f"Error deleting file {filePath}: {e}")
    else:
        print(f"Folder {folderPath} does not exist.")  

if __name__ == "__main__":
    # Ensure directories exist before starting
    # getSessionList()
    ensure_directories()
    getMasterList()
    # emptyBillTextFolder()
