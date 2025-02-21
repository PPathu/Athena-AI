import requests
from keys import legiscanKey
import json

STATE = "WI"

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
def getMasterList():
  # Could change this to be based on session id instead of state
  url = f"https://api.legiscan.com/?key={legiscanKey}&op=getMasterList&state={STATE}"
  response = requests.get(url) 
  if response.status_code == 200:
    data = response.json()
    if 'masterlist' in data:
      print("\n Available Wisconsin Bills:")
      bills = sorted(data['masterlist'].values(), key=lambda x: x.get('status_date', ''), reverse=True)
      billList = []
      for bill in bills:
        billData = {
          "billNumber": bill.get('number', 'UNKNOWN'),
          "billId": bill.get('bill_id', 'UNKNOWN'),
          "billStatusDate": bill.get('status_date', 'UNKNOWN'),
          "billStatus": bill.get('status', 'UNKNOWN'),
          "billTitle": bill.get('title', 'UNKNOWN'),
          "billDescription": bill.get('description', 'UNKNOWN')
        }
        billList.append(billData)
      outputFile = 'data.json'
      with open(outputFile, "w", encoding="utf-8") as f:
        json.dump(billList, f, indent=4)
            
      print(f"Bill data saved to {outputFile}")
      return billList  

  print("\n ERROR: Failed to fetch master list.")
  return []
  
if __name__ == "__main__":
  # getSessionList()
  getMasterList()
  