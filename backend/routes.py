from flask import Blueprint, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get Supabase URL and Key from the environment variables
SUPABASE_URL = os.getenv("REACT_APP_SUPABASE_URL")
SUPABASE_KEY = os.getenv("REACT_APP_SUPABASE_ANON_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize Blueprint
bill_routes = Blueprint("bill_routes", __name__)

# This route gets all bill attributes that appear in the enhanced data database and returns them as a json for the frontend to use
@bill_routes.route("/getBills", methods=["GET"])
def get_bills():
    try:
        response = supabase.table("enhanceddata").select("*").execute()
        bills = response.data 
        error = response.error if hasattr(response, "error") else None
        if error:
            return jsonify({"error": str(error)}), 500
        if not bills:
            return jsonify({"message": "No bills found."}), 404
        return jsonify(bills)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
