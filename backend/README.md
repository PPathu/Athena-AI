# Athena AI Backend Server

This server hosts both the API endpoints and serves the frontend application.

## Setup

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Make sure you have Node.js installed for frontend builds.

## Running the Server

To start the server with automatic frontend build:

```
python start_server.py
```

To skip the frontend build (if you already built it):

```
python start_server.py --skip-build
```

Once running, access the application at: http://localhost:5000

## API Endpoints

- `GET /api/bills` - Get all bills
- Frontend application: `/app`
