import requests

response = requests.post("http://127.0.0.1:5000/api/chat", json={
    "bill_id": "1977778",
    "question": "What is the main purpose of Bill 1977778?"
})

print("Response from API:")
print(response.json())
