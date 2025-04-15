from flask import Blueprint, jsonify, request
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
        # Fetch all bills with related AI summaries
        response = supabase.table("enhanceddata").select(
            "*, ai_summaries_enhanced(response, response_simple, response_intermediate, response_persuasive, response_pros_cons, response_tweet, desc_response)"
        ).execute()

        error = response.error if hasattr(response, "error") else None
        bills = response.data

        if error:
            return jsonify({"error": str(error)}), 500
        if not bills:
            return jsonify({"message": "No bills found."}), 404

        # For each bill, keep only the first ai_summaries_enhanced entry if it exists
        for bill in bills:
            if "ai_summaries_enhanced" in bill and isinstance(bill["ai_summaries_enhanced"], list):
                bill["ai_summaries_enhanced"] = bill["ai_summaries_enhanced"][0] if bill["ai_summaries_enhanced"] else None

        return jsonify(bills)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Gets basic enhanced data table data for the paginated pages (url format: http://localhost:5000/getBills/paginated?page=2&per_page=5)
@bill_routes.route("/getBills/paginated", methods=["GET"])
def get_paginated_bills():
    try:
        print(request)  # Debugging step
        print(request.args)  # This should be an ImmutableMultiDict

        page = request.args.get('page', default=1, type=int)
        bills_per_page = request.args.get('per_page', default=10, type=int)
        # Calculate range
        start_idx = (page - 1) * bills_per_page
        end_idx = (page * bills_per_page) - 1
        
        # Build and execute the query
        response = (
            supabase
            .from_("enhanceddata")
            .select("""
                *,
                ai_summaries_enhanced:ai_summaries_enhanced(
                    desc_response, 
                    response
                )
            """)
            .range(start_idx, end_idx)
            .execute()
        )
        
        bills = response.data
        
        if not bills:
            return jsonify({
                "message": "No bills found for this page.",
                "data": [],
                "page": page,
                "per_page": bills_per_page
            }), 404
            
        return jsonify({
            "data": bills,
            "page": page,
            "per_page": bills_per_page,
            "total_count": len(bills)  # Note: For total count you'd need a separate count query
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# example (url format: http://localhost:5000/getBillById?bill_id=1952554)
@bill_routes.route("/getBillById", methods=["GET"])
def get_bill_by_id():
    try:
        bill_id = request.args.get("bill_id")
        if not bill_id:
            return jsonify({"error": "Missing 'bill_id' query parameter."}), 400

        # Fetch the specific bill and related AI summaries
        response = supabase.table("enhanceddata").select(
            "*, ai_summaries_enhanced(response, response_simple, response_intermediate, response_persuasive, response_pros_cons, response_tweet, desc_response)"
        ).eq("bill_id", bill_id).execute()

        error = response.error if hasattr(response, "error") else None
        bills = response.data

        if error:
            return jsonify({"error": str(error)}), 500
        if not bills:
            return jsonify({"message": f"No bill found with bill_id '{bill_id}'."}), 404

        bill = bills[0]

        # Keep only the first AI summary (if it exists)
        if "ai_summaries_enhanced" in bill and isinstance(bill["ai_summaries_enhanced"], list):
            bill["ai_summaries_enhanced"] = bill["ai_summaries_enhanced"][0] if bill["ai_summaries_enhanced"] else None

        return jsonify(bill)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
