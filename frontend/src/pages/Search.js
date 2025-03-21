import React, { useState, useEffect } from "react";
import supabase from "../utils/supabase";
import "../styles/styles.css";

function toTitleCase(str) {
  if (!str) return "";
  return str.replace(/\w\S*/g, (txt) => {
    return txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase();
  });
}

function capitalizeSentences(text) {
  if (!text) return "";
  const sentences = text.split(/(?<=[.!?])\s+/);
  return sentences.map(sentence => sentence.charAt(0).toUpperCase() + sentence.slice(1)).join(" ");
}

function formatAiSummary(rawText) {
  if (!rawText) return "No AI summary available.";
  let processed = rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  return capitalizeSentences(processed);
}

const Search = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [selectedBill, setSelectedBill] = useState(null);
  const billsPerPage = 6;

  const getTwoSentenceSummary = (text) => {
    if (!text) return "No description available.";
    const capitalized = capitalizeSentences(text);
    const sentences = capitalized.split(/(?<=[.!?])\s+/);
    return sentences.slice(0, 2).join(" ");
  };

  const fetchBills = async () => {
    setLoading(true);
    setError("");

    try {
      let query = supabase
        .from("enhanceddata")
        .select("*, ai_summaries_enhanced:ai_summaries_enhanced(response)")
        .range((page - 1) * billsPerPage, page * billsPerPage - 1);

      if (searchTerm.trim()) {
        query = query.ilike("title", `%${searchTerm}%`);
      }

      const { data, error } = await query;
      if (error) throw error;

      setBills(data);
    } catch (err) {
      setError("Failed to fetch bills. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills();
  }, [page]);

  const openModal = (bill) => {
    setSelectedBill(bill);
  };

  const closeModal = () => {
    setSelectedBill(null);
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
              <h3>{toTitleCase(bill.title)}</h3>
              <p className="bill-description">{getTwoSentenceSummary(bill.description)}</p>
              <button className="learn-more-btn" onClick={() => openModal(bill)}>
                Learn More
              </button>
            </div>
          ))
        ) : (
          <p className="no-results">No matching bills found.</p>
        )}
      </div>

      <div className="pagination">
        {page > 1 && <button onClick={() => setPage(page - 1)}>Previous</button>}
        {bills.length === billsPerPage && <button onClick={() => setPage(page + 1)}>Next</button>}
      </div>

      {selectedBill && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={closeModal} className="close-btn">&times;</button>
            <h2>{toTitleCase(selectedBill.title)}</h2>
            <div className="official-description">
              <h4>Official Description</h4>
              <p>{capitalizeSentences(selectedBill.description)}</p>
            </div>
            <div className="status-details">
              <p><strong>Bill Status:</strong> {selectedBill.status || "N/A"}</p>
              <p><strong>Last Action:</strong> {selectedBill.last_action || "N/A"}</p>
            </div>
            <div className="ai-summary">
              <h4>AI Summary</h4>
              <div dangerouslySetInnerHTML={{ __html: formatAiSummary(selectedBill.ai_summaries_enhanced?.[0]?.response || "") }} />
            </div>
            <div className="bill-history">
              <h4>History</h4>
              <ul className="bill-history-list">
                {selectedBill.history ? selectedBill.history.split(";").map((entry, idx) => {
                  const [datePart, ...rest] = entry.trim().split(" - ");
                  return (
                    <li key={idx}>
                      <span className="bill-history-date">{datePart}</span>
                      <span className="bill-history-description">{rest.join(" - ")}</span>
                    </li>
                  );
                }) : <p>No history available.</p>}
              </ul>
            </div>
            <a href={selectedBill.url} target="_blank" rel="noopener noreferrer" className="view-full-bill-link">
              View Full Bill
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;
