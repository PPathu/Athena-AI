import os
from flask import Blueprint, request, jsonify
import google.generativeai as genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from supabase import create_client

# Added by nicole to get .env info 
from dotenv import load_dotenv
load_dotenv()
#config
bill_routes = Blueprint("bill_routes", __name__)

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found in environment variables.")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

#load bills into vector store
try:
    response = supabase.table("enhanceddata").select("*").execute()
    data = response.data
except Exception as e:
    print("Error fetching from Supabase:", e)
    data = []

documents = []
for bill in data:
    doc_text = (
        f"Bill ID: {bill.get('bill_id', 'N/A')}\n"
        f"Title: {bill.get('title', 'N/A')}\n"
        f"Description: {bill.get('description', 'N/A')}\n"
        f"Status: {bill.get('status', 'N/A')}\n"
        f"Last Action: {bill.get('last_action', 'N/A')}\n"
        f"History: {bill.get('history', 'N/A')}\n"
        f"Sponsor: {bill.get('sponsor_name', 'N/A')} ({bill.get('sponsor_party', 'N/A')})\n"
        f"URL: {bill.get('url', 'N/A')}\n"
    )
    documents.append(Document(page_content=doc_text, metadata={"bill_id": bill.get("bill_id", "unknown")}))

print(f"Loaded {len(documents)} bill documents into memory.")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(documents, embeddings)

def retrieve_context(query, bill_id, k=3):
    k = int(k)
    filtered_docs = [doc for doc in documents if doc.metadata.get("bill_id") == bill_id]
    if not filtered_docs:
        return ["No relevant documents found for this bill."]
    local_vector_store = FAISS.from_documents(filtered_docs, embeddings)
    return [doc.page_content for doc in local_vector_store.similarity_search(query, k=k)]

#api route
@bill_routes.route("/api/chat", methods=["POST"])
def chat():
    print("Received POST to /api/chat")
    print("Headers:", dict(request.headers))
    print("Raw body:", request.data)

    try:
        data = request.get_json(force=True)
    except Exception as e:
        print("JSON parse error:", e)
        return jsonify({"error": "Invalid JSON"}), 400

    bill_id = data.get("bill_id")
    question = data.get("question")

    if not bill_id or not question:
        return jsonify({"error": "bill_id and question are required"}), 400

    context_docs = retrieve_context(question, bill_id)
    context = "\n".join(context_docs)

    prompt = (
        f"Using the following legislative bill context, answer the question with citations:\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        answer = response.text.strip() if hasattr(response, "text") else "No answer generated."
        return jsonify({"answer": answer})
    except Exception as e:
        print("Gemini error:", e)
        return jsonify({"error": f"Failed to generate answer: {e}"}), 500

