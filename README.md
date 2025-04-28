# Athena-AI

Athena AI is a legislative summarization website that leverages large language models to turn dense legislative data into clear, short summaries. We scrape and store bill details in our database, then generate multiple summary styles (simple overviews, mid-level explanations, persuasive “why it matters” pitches, pros/cons lists, and tweet-styled summaries). Users can also ask natural language questions about a specific bill and receive concise, factual responses powered by a RAG pipeline using Gemini.


## 🛠 Tech Stack

- **Frontend**: React, Webpack
- **Backend**: Flask (Python)
- **AI Integration**: Google Gemini API
- **Database**: Supabase
- **Vector Store**: FAISS (via LangChain)

## Getting Started

This project requires you run 2 terminals.  One for the front end and one for the backend. 

# Environment Variables

Make sure you have the following in a .env file before trying to run the backend

Install: pip install python-dotenv

GEMINI_API_KEY=your_gemini_api_key

REACT_APP_SUPABASE_URL=https://your-project.supabase.co

REACT_APP_SUPABASE_ANON_KEY=your_supabase_anon_key


# Backend / Flask Server

- Navigate to backend: cd backend 
- Install requirements: pip install -r requirements.txt
- Start flask server: python app.py
- Flask server should start at: http://127.0.0.1:5000 


# Frontend 
- Navigate to frontend: cd frontend
- Start app: npm start
- Front end should start at: http://localhost:3000


Important: The frontend relies on this API to function. If this isn’t running, the UI won’t be able to fetch AI responses, and you’ll see CORS or “Failed to fetch” errors in the browser.
