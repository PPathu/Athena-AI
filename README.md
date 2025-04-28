# Athena AI
Athena AI is a legislative summarization website that leverages large language models to turn dense legislative data into clear, short summaries. We scrape and store bill details in our database, then generate multiple summary styles (simple overviews, mid-level explanations, persuasive “why it matters” pitches, pros/cons lists, and tweet-styled summaries). Users can also ask natural language questions about a specific bill and receive concise, factual responses powered by a RAG pipeline using Gemini.
---
## :hammer_and_wrench: Tech Stack
- **Frontend**: React, Webpack 
- **Backend**: Flask (Python) 
- **AI Integration**: Google Gemini API 
- **Database**: Supabase 
- **Vector Store**: FAISS (via LangChain)
---
## :rocket: Getting Started
This project requires running **two terminals** — one for the frontend and one for the backend.

### Backend
- Move to the backend: cd backend
- Install dependencies: pip install -r requirments.txt
- Start server: python app.py
- Server should start at http://127.0.0.1:5000

### Frontend
- Move to frontend: cd frontend
- Install dependencies: npm install
- Start frontend: npm start
- Frontend should start at http://127.0.0.1:3000

---
## :package: Environment Variables
Make sure you have the following in a `.env` file **before** running the backend.
