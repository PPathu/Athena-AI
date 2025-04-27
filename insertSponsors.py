import os
import json
from dotenv import load_dotenv, find_dotenv
from supabase import create_client, Client
from typing import Optional

def connect_supabase() -> Client:
    """Reads Supabase creds from .env and returns a client."""
    load_dotenv(find_dotenv())

    url = os.getenv("REACT_APP_SUPABASE_URL")
    key = os.getenv("REACT_APP_SUPABASE_ANON_KEY")
    if not url or not key:
        raise SystemExit("Missing REACT_APP_SUPABASE_URL or REACT_APP_SUPABASE_ANON_KEY in .env")

    print("Supabase client configured")
    return create_client(url, key)

def insert_sponsors_from_json(
    supabase: Client,
    json_path: str,
    bill_id_filter: Optional[str] = None
) -> None:
    """
    Reads a JSON list of {billId, sponsors} entries and updates enhanceddata.sponsors
    in Supabase for each matching billId. If bill_id_filter is set, only that one is updated.
    """
    with open(json_path, "r") as f:
        bills_data = json.load(f)

    for bill in bills_data:
        bill_id  = bill.get("billId")
        sponsors = bill.get("sponsors")

        # skip ones that don't match the filter (if provided)
        if bill_id_filter and str(bill_id) != str(bill_id_filter):
            continue

        if not bill_id:
            print("Skipping entry missing billId")
            continue
        if not sponsors:
            print(f"Skipping bill {bill_id}: no sponsors array")
            continue

        resp = (
            supabase
              .table("enhanceddata")
              .update({"sponsors": sponsors})
              .eq("bill_id", bill_id)
              .execute()
        )

        # resp.data is the list of updated rows
        if resp.data and len(resp.data) > 0:
            print(f"Updated sponsors for bill {bill_id}")
        else:
            print(f"No rows updated for bill {bill_id} (resp.data is empty)")

if __name__ == "__main__":
    supabase = connect_supabase()
    insert_sponsors_from_json(supabase, "NEWdata.json")
    print("Done.")
