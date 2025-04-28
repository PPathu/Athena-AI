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

## Environment Variables

Make sure you have the following in a .env file before trying to run the backend

Install: pip install python-dotenv

LEGISCAN_API_KEY=

userkey=

DATABASE_URL=

GEMINI_API_KEY=

REACT_APP_SUPABASE_URL=

REACT_APP_SUPABASE_ANON_KEY=

The LEGISCAN_API_KEY (along with the LEGISCAN_USER_KEY) comes from our LegiScan account; both values identify the same LegiScan user that we used when scraping bill data. The DATABASE_URL is the Postgres connection pool endpoint that Supabase provides for our project.mThe GEMINI_API_KEY was what we used to generate the first batch of AI summaries before we switched to the Google Cloud credits. The REACT_APP_SUPABASE_URL points to our Supabase project, and the SUPABASE_ANON_KEY is the project’s public “anon” JWT key that every client shares. (It is project wide, not one per user; verified users still sign in, but they all send the same anon key)

### Backend / Flask Server

- Navigate to backend: cd backend 
- Install requirements: pip install -r requirements.txt
- Start flask server: python app.py
- Flask server should start at: http://127.0.0.1:5000 


### Frontend 
- Navigate to frontend: cd frontend
- Start app: npm start
- Front end should start at: http://localhost:3000


Important: The frontend relies on this API to function. If this isn’t running, the UI won’t be able to fetch AI responses, and you’ll see CORS or “Failed to fetch” errors in the browser.


## Future Work

### What works 
Our multi-style summaries are clear and accurate, keyword search reliably surfaces the right bills, the new random bill feature encourages exploration, and the Ask-AI panel usually returns concise, relevant answers.

### What doesn’t work 
The RAG pipeline currently feeds Gemini only a small slice of each bill - title, status, descriptions, etc. - so answers can lack depth. We still exclude important context such as full text, fiscal notes, committee reports, and news coverage. We also have no analytics to show which summary modes or queries users value most.

### Next feature to build
Expand the RAG pipeline so the AI can draw on the full bill text plus supporting material (committee reports, sponsor statements, trusted news articles, etc). That richer corpus would be batched, embedded, stored in FAISS, and passed to Gemini in a larger context window. The result would be deeper, more precise answers and the ability to explain why a bill advanced, who supports or opposes it, and how the public views it.
