import React, { useState, useEffect } from "react";
import supabase from "../utils/supabase";
import "../styles/styles.css";

const Search = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [expandedBill, setExpandedBill] = useState(null);
  const [page, setPage] = useState(1);
  const billsPerPage = 6; //adjust how many bills per page

  //get bills from Supabase based on search term and page
  const fetchBills = async () => {
    setLoading(true);
    setError("");

    try {
      console.log("🔎 Searching for:", searchTerm);

      let query = supabase
        .from("enhanceddata")
        .select("*")
        .range((page - 1) * billsPerPage, page * billsPerPage - 1);

      if (searchTerm.trim()) {
        query = query.ilike("title", `%${searchTerm}%`); //case-insensitive search
      }

      const { data, error } = await query;
      if (error) throw error;

      console.log("Bills from Supabase:", data);
      setBills(data);
    } catch (err) {
      console.error("Supabase Fetch Error:", err);
      setError("Failed to fetch bills - try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills(); //get bills on page load and when search term changes
  }, [page]);

  //toggle bill details view
  const toggleBillDetails = (billId) => {
    setExpandedBill(expandedBill === billId ? null : billId);
  };

  return (
    <div className="search-container">
      <h2>Search Bills</h2>
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search bills..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={fetchBills}>Search</button>
      </div>

      {loading && <p className="loading-text">Loading bills...</p>}
      {error && <p className="error-message">{error}</p>}

      <div className="bill-list">
        {bills.length > 0 ? (
          bills.map((bill) => (
            <div key={bill.id} className="bill-card">
              <h3>{bill.title}</h3>
              <p className="bill-description">
                {bill.description.length > 100
                  ? `${bill.description.substring(0, 100)}...`
                  : bill.description}
              </p>
              <p className="bill-summary">
                <strong>Summary:</strong>{" "}
                {bill.ai_summary
                  ? bill.ai_summary.length > 120
                    ? `${bill.ai_summary.substring(0, 120)}...`
                    : bill.ai_summary
                  : "No summary available"}
              </p>
              <button onClick={() => toggleBillDetails(bill.id)}>
                {expandedBill === bill.id ? "Show Less" : "Read More"}
              </button>

              {expandedBill === bill.id && (
                <div className="bill-details">
                  <p><strong>Status:</strong> {bill.status}</p>
                  <p><strong>Last Action:</strong> {bill.last_action}</p>
                  <p><strong>History:</strong> {bill.history}</p>
                  <p><strong>Full Summary:</strong> {bill.ai_summary || "No AI summary available"}</p>
                  <a href={bill.url} target="_blank" rel="noopener noreferrer">
                    View Full Bill
                  </a>
                </div>
              )}
            </div>
          ))
        ) : (
          <p className="no-results">No matching bills found.</p>
        )}
      </div>

      {/*pagination controls*/}
      <div className="pagination">
        {page > 1 && <button onClick={() => setPage(page - 1)}>Previous</button>}
        {bills.length === billsPerPage && <button onClick={() => setPage(page + 1)}>Next</button>}
      </div>
    </div>
  );
};

export default Search;
