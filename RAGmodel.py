import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document

# Disable parallel tokenizer fork warnings
os.environ["TOKENIZERS_PARALLELISM"] = "false"

app = Flask(__name__)

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Initialize HuggingFace embeddings (or use your preferred model)
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Example documents
documents = [
    Document(
        page_content=(
            "Bill 1977778: An act to regulate legislative summary generation. "
            "Key points include enhanced transparency and accountability. "
            "Citation: https://legislature.gov/bill1977778"
        ),
        metadata={"bill_id": "1977778"}
    ),
    Document(
        page_content=(
            "Bill 1952554: An act to improve transparency in legislative processes. "
            "This bill introduces new disclosure requirements. "
            "Citation: https://legislature.gov/bill1952554"
        ),
        metadata={"bill_id": "1952554"}
    ),
    # Add more documents as needed...
]

# Build FAISS vector store
vector_store = FAISS.from_documents(documents, embeddings)

def retrieve_context(query, k=3):
    results = vector_store.similarity_search(query, k=k)
    return [doc.page_content for doc in results]

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    bill_id = data.get("bill_id")
    question = data.get("question")

    if not bill_id or not question:
        return jsonify({"error": "bill_id and question are required"}), 400

    context_docs = retrieve_context(question)
    context = "\n".join(context_docs)

    prompt = (
        f"Using the following context from the bill documents, answer the question with citations:\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer with citations:"
    )

    try:
        response = genai.GenerativeModel("gemini-1.5-pro").generate_content(prompt)
        answer = response.text if response and hasattr(response, "text") else "No answer generated."
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": f"Failed to generate answer: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
