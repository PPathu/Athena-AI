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
  // split on sentence-ending punctuation + whitespace
  const sentences = text.split(/(?<=[.!?])\s+/);
  const capitalized = sentences.map((sentence) => {
    const trimmed = sentence.trim();
    if (!trimmed) return "";
    return trimmed.charAt(0).toUpperCase() + trimmed.slice(1);
  });
  return capitalized.join(" ");
}

function formatAiSummary(rawText) {
  if (!rawText) return "No AI summary available.";
  //replace double-asterisks with <strong> tags
  let processed = rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  processed = capitalizeSentences(processed);
  return processed;
}

const Search = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [selectedBill, setSelectedBill] = useState(null);
  const billsPerPage = 6;

  //helper to get a short summary from the bill description
  const getTwoSentenceSummary = (text) => {
    if (!text) return "No description available.";
    //capitalize each sentence, then only take the first two
    const capitalized = capitalizeSentences(text);
    const sentences = capitalized.split(/(?<=[.!?])\s+/);
    return sentences.slice(0, 2).join(" ");
  };

  const fetchBills = async () => {
    setLoading(true);
    setError("");

    try {
      console.log("Searching for:", searchTerm);
      let query = supabase
        .from("enhanceddata")
        .select("*, ai_summaries_enhanced:ai_summaries_enhanced(response)")
        .range((page - 1) * billsPerPage, page * billsPerPage - 1);

      if (searchTerm.trim()) {
        query = query.ilike("title", `%${searchTerm}%`);
      }

      const { data, error } = await query;
      if (error) throw error;

      console.log("Bills from Supabase:", data);
      setBills(data);
    } catch (err) {
      console.error("Supabase fetch error:", err);
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

  // Example sponsor info (replace with real sponsor logic or DB columns)
  const getSponsorsForBill = (bill) => {
    // In your JSON, you have sponsor_name, sponsor_party, sponsor_role, etc.
    // You can store them in the DB or compute them from the AI summary.
    if (!bill.sponsor_name) {
      return [];
    }
    return [
      {
        name: capitalizeSentences(bill.sponsor_name),
        party: bill.sponsor_party?.toUpperCase() || "Unknown",
      },
    ];
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
          bills.map((bill) => {
            const shortSummary = getTwoSentenceSummary(bill.description);
            // Convert the bill title to title case
            const displayedTitle = toTitleCase(bill.title);

            return (
              <div key={bill.id} className="bill-card">
                <h3>{displayedTitle}</h3>
                <p className="bill-description">{shortSummary}</p>
                <button className="learn-more-btn" onClick={() => openModal(bill)}>
                  Learn More
                </button>
              </div>
            );
          })
        ) : (
          <p className="no-results">No matching bills found.</p>
        )}
      </div>

      <div className="pagination">
        {page > 1 && (
          <button onClick={() => setPage(page - 1)}>Previous</button>
        )}
        {bills.length === billsPerPage && (
          <button onClick={() => setPage(page + 1)}>Next</button>
        )}
      </div>

      {/* Modal */}
      {selectedBill && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={closeModal} className="close-btn">
              &times;
            </button>

            {/* Title (in Title Case) */}
            <h2>{toTitleCase(selectedBill.title)}</h2>

            {/* Official Description */}
            <div className="official-description">
              <h4>Official Description</h4>
              <p>{capitalizeSentences(selectedBill.description)}</p>
            </div>

            {/* Bill Status */}
            <div className="status-details">
              <p>
                <strong>Bill Status:</strong> {selectedBill.status || "N/A"}
              </p>
              <p>
                <strong>Last Action:</strong> {selectedBill.last_action || "N/A"}
              </p>
            </div>

            {/* AI Summary */}
            <div className="ai-summary">
              <h4>AI Summary</h4>
              {selectedBill.ai_summaries_enhanced?.[0]?.response ? (
                <div
                  dangerouslySetInnerHTML={{
                    __html: formatAiSummary(selectedBill.ai_summaries_enhanced[0].response),
                  }}
                />
              ) : (
                <p>No AI summary available.</p>
              )}
            </div>

            {/* Sponsors */}
            <div className="sponsors">
              <h4>Sponsor Information</h4>
              <table className="sponsors-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Party</th>
                  </tr>
                </thead>
                <tbody>
                  {getSponsorsForBill(selectedBill).map((s, idx) => (
                    <tr key={idx}>
                      <td>{s.name}</td>
                      <td>{s.party}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* History */}
            <div className="bill-history">
              <h4>History</h4>
              <p>{selectedBill.history || "No history available."}</p>
            </div>

            {/* Full Bill Link */}
            <a
              href={selectedBill.url}
              target="_blank"
              rel="noopener noreferrer"
              className="view-full-bill-link"
            >
              View Full Bill
            </a>
          </div>
        </div>
      )}
    </div>
  );
};

export default Search;
