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
  const billsPerPage = 6; // Adjust how many bills per page

  // Fetch bills from Supabase, joining with AI summaries
  const fetchBills = async () => {
    setLoading(true);
    setError("");

    try {
      console.log("🔎 Searching for:", searchTerm);

      let query = supabase
        .from("enhanceddata")
        .select(
          "*, ai_summaries_enhanced:ai_summaries_enhanced(response)" // Join ai_summaries_enhanced by aliasing it
        )
        .range((page - 1) * billsPerPage, page * billsPerPage - 1);

      if (searchTerm.trim()) {
        query = query.ilike("title", `%${searchTerm}%`); // Case-insensitive search
      }

      const { data, error } = await query;
      if (error) throw error;

      console.log("✅ Bills from Supabase:", data);
      setBills(data);
    } catch (err) {
      console.error("❌ Supabase Fetch Error:", err);
      setError("Failed to fetch bills. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills(); // Fetch bills when page changes
  }, [page]);

  // Toggle bill details view
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
                {bill.description && bill.description.length > 100
                  ? `${bill.description.substring(0, 100)}...`
                  : bill.description || "No description available"}
              </p>
              <p className="bill-summary">
              <strong>AI Summary:</strong>
              <br />
              {bill.ai_summaries_enhanced?.[0]?.response &&
              !bill.ai_summaries_enhanced[0].response.includes("Since the title and description of the bill are unknown")
                ? bill.ai_summaries_enhanced[0].response
                    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>") // Convert markdown **bold** to HTML <strong>
                    .replace(/\n/g, "<br />") // Ensure proper spacing between paragraphs
                    .replace(/\* (.*?)/g, "• $1") // Convert markdown * bullet points to •
                : "No AI summary available"}
            </p>



              <button onClick={() => toggleBillDetails(bill.id)}>
                {expandedBill === bill.id ? "Show Less" : "Read More"}
              </button>

              {expandedBill === bill.id && (
                <div className="bill-details">
                  <p><strong>Status:</strong> {bill.status}</p>
                  <p><strong>Last Action:</strong> {bill.last_action}</p>
                  <div>
                    <strong>History:</strong>
                    <ul className="bill-history-list">
                      {bill.history.split(";").map((entry, idx) => {
                        // Split "YYYY-MM-DD - Some text" into [date, restOfLine]
                        const [datePart, ...rest] = entry.trim().split(" - ");
                        return (
                          <li key={idx}>
                            <span className="bill-history-date">{datePart}</span>
                            <span className="bill-history-description">
                              {rest.join(" - ")}
                            </span>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                  <p><strong>Full Summary:</strong> {bill.ai_summaries_enhanced?.[0]?.response || "No AI summary available"}</p>
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

      {/* Pagination controls */}
      <div className="pagination">
        {page > 1 && <button onClick={() => setPage(page - 1)}>Previous</button>}
        {bills.length === billsPerPage && <button onClick={() => setPage(page + 1)}>Next</button>}
      </div>
    </div>
  );
};

export default Search;
