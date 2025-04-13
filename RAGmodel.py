import os
from flask import Flask, request, jsonify
from flask_cors import CORS

import google.generativeai as genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from supabase import create_client, Client

#app setup
app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase URL or key is missing in environment variables.")


#supabase fetch
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    response = supabase.table("enhanceddata").select("*").execute()
    data = response.data
except Exception as e:
    print("Error fetching documents:", e)
    data = []

documents = []
for bill in data:
    doc_text = (
        f"Bill ID: {bill.get('bill_id', 'N/A')}\n"
        f"Bill Number: {bill.get('bill_number', 'N/A')}\n"
        f"Session: {bill.get('session', 'N/A')}\n"
        f"Title: {bill.get('title', 'N/A')}\n"
        f"Description: {bill.get('description', 'N/A')}\n"
        f"Status: {bill.get('status', 'N/A')}\n"
        f"Status Date: {bill.get('statusDate', 'N/A')}\n"
        f"Last Action: {bill.get('last_action', 'N/A')}\n"
        f"Last Action Date: {bill.get('last_action_date', 'N/A')}\n"
        f"URL: {bill.get('url', 'N/A')}\n"
        f"PDF Link: {bill.get('pdf_link', 'N/A')}\n"
        f"TXT Link: {bill.get('txt_link', 'N/A')}\n"
        f"Amendments: {bill.get('amendments', 'N/A')}\n"
        f"Amendment Links: {bill.get('amendment_links', 'N/A')}\n"
        f"See Also: {bill.get('see_also', 'N/A')}\n"
        f"History: {bill.get('history', 'N/A')}\n"
        f"Sponsor Name: {bill.get('sponsor_name', 'N/A')}\n"
        f"Sponsor Party: {bill.get('sponsor_party', 'N/A')}\n"
        f"Sponsor Role: {bill.get('sponsor_role', 'N/A')}\n"
        f"Sponsor Type: {bill.get('sponsor_type', 'N/A')}\n"
        f"Sponsor Order: {bill.get('sponsor_order', 'N/A')}\n"
    )
    documents.append(Document(page_content=doc_text, metadata={"bill_id": bill.get("bill_id", "unknown")}))

print(f"Retrieved {len(documents)} documents from the database.")

#FAISS vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(documents, embeddings)

def retrieve_context(query, k=3):
    results = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]

#api/chat endpoint
@app.route('/api/chat', methods=['POST'])
def chat():
    print("Received POST to /api/chat")
    print("Headers:", dict(request.headers))
    print("Raw body:", request.data)

    try:
        data = request.get_json(force=True)
        print("Parsed JSON:", data)
    except Exception as e:
        print("JSON parse error:", e)
        return jsonify({"error": "Invalid JSON"}), 400

    bill_id = data.get("bill_id")
    question = data.get("question")

    if not bill_id or not question:
        return jsonify({"error": "bill_id and question are required"}), 400

    context_docs = retrieve_context(question)
    context = "\n".join(context_docs)

    prompt = (
    f"You are a legislative assistant AI. Based only on the following context, answer the question directly, concisely, and factually. "
    f"Do not include any formatting (Markdown, HTML, bullet points, or special characters). "
    f"Do not repeat the question. Do not say 'Based on the context' or provide unnecessary disclaimers. "
    f"Just state the answer clearly and objectively.\n\n"
    f"Answer:"
)

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        answer = response.text if response and hasattr(response, "text") else "No answer generated."
        return jsonify({"answer": answer})
    except Exception as e:
        print("Gemini error:", e)
        return jsonify({"error": f"Failed to generate answer: {e}"}), 500

#run server
if __name__ == "__main__":
    app.run(debug=True, port=5000)
