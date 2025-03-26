import React, { useState, useEffect } from "react";
import supabase from "../utils/supabase";
import "../styles/styles.css";

/** 
 * Convert a string to Title Case 
 */
function toTitleCase(str) {
  if (!str) return "";
  return str.replace(/\w\S*/g, (txt) => {
    return txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase();
  });
}

/** 
 * Capitalize the first letter of each sentence. 
 */
function capitalizeSentences(text) {
  if (!text) return "";
  const sentences = text.split(/(?<=[.!?])\s+/);
  return sentences
    .map(
      (sentence) =>
        sentence.charAt(0).toUpperCase() + sentence.slice(1).toLowerCase()
    )
    .join(" ");
}

/** 
 * Convert simple Markdown-like bold (**word**) into HTML <strong> 
 * and then capitalize sentences. 
 */
function formatAiSummary(rawText) {
  if (!rawText) return "No AI summary available.";
  const replaced = rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  return capitalizeSentences(replaced);
}

/**
 * Return the first two sentences from some text, capitalizing them.
 */
function getTwoSentenceSummary(text) {
  if (!text) return "No description available.";
  const capitalized = capitalizeSentences(text);
  const sentences = capitalized.split(/(?<=[.!?])\s+/);
  return sentences.slice(0, 2).join(" ");
}

const Search = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [selectedBill, setSelectedBill] = useState(null);
  const [selectedMode, setSelectedMode] = useState("response_simple"); // example mode

  const billsPerPage = 6;

  /**
   * Fetch bills from Supabase. We select both the “desc_response” (AI's short 
   * description) and “response” (longer summary) from the “ai_summaries_enhanced” table. 
   */
  const fetchBills = async () => {
    setLoading(true);
    setError("");

    try {
      console.log("Searching for:", searchTerm);

      let query = supabase
        .from("enhanceddata")
        .select(`
          *,
          ai_summaries_enhanced:ai_summaries_enhanced(desc_response, response)
        `) // pulling in both columns
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

  /** 
   * Show the modal with details for a chosen bill. 
   * Reset the mode dropdown if desired.
   */
  const openModal = (bill) => {
    setSelectedBill(bill);
    setSelectedMode("response_simple"); // default to a "simple" mode
  };

  const closeModal = () => {
    setSelectedBill(null);
  };

  const handleModeChange = (e) => {
    setSelectedMode(e.target.value);
  };

  return (
    <div className="search-container">
      <h2>Search Bills</h2>

      {/* Search bar */}
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search bills..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <button onClick={fetchBills}>Search</button>
      </div>

      {/* Loading / Error */}
      {loading && <p className="loading-text">Loading bills...</p>}
      {error && <p className="error-message">{error}</p>}

      {/* Bill list: each card shows short text */}
      <div className="bill-list">
        {bills.length > 0 ? (
          bills.map((bill) => {
            // If there's an AI short description, use it; otherwise fallback to bill.description
            const shortDesc =
              bill.ai_summaries_enhanced?.[0]?.desc_response ||
              bill.description ||
              "No description available.";

            return (
              <div key={bill.id} className="bill-card">
                <h3>{toTitleCase(bill.title)}</h3>
                <p className="bill-description">
                  {getTwoSentenceSummary(shortDesc)}
                </p>
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

      {/* Pagination controls */}
      <div className="pagination" style={{ marginBottom: "40px" }}>
        {page > 1 && (
          <button onClick={() => setPage(page - 1)}>Previous</button>
        )}
        {bills.length === billsPerPage && (
          <button onClick={() => setPage(page + 1)}>Next</button>
        )}
      </div>

      {/* Modal for expanded details */}
      {selectedBill && (
        <div className="modal-overlay">
          <div className="modal-content">
            {/* close button */}
            <button onClick={closeModal} className="close-btn">
              &times;
            </button>

            {/* Bill title */}
            <h2>{toTitleCase(selectedBill.title)}</h2>

            {/* Official Description (Full AI short description or the original bill.description) */}
            <div className="official-description" style={{ background: "#eff6ff", padding: "10px", borderRadius: "4px" }}>
              <h4>Official Description</h4>
              <p>
                {
                  capitalizeSentences(
                    selectedBill.ai_summaries_enhanced?.[0]?.desc_response ||
                    selectedBill.description ||
                    "No description available."
                  )
                }
              </p>
            </div>

            {/* Bill status */}
            <div className="status-details" style={{ marginTop: "10px" }}>
              <p>
                <strong>Bill Status:</strong> {selectedBill.status || "N/A"}
              </p>
              <p>
                <strong>Last Action:</strong> {selectedBill.last_action || "N/A"}
              </p>
            </div>

            {/* AI Summary with dropdown modes */}
            <div className="ai-summary" style={{ marginTop: "15px" }}>
              <h4>AI Summary (Detailed)</h4>
              {/* Mode selection */}
              <div style={{ marginBottom: "8px" }}>
                <select value={selectedMode} onChange={handleModeChange}>
                  <option value="response_simple">Simple & Clear</option>
                  <option value="response_intermediate">Straightforward</option>
                  <option value="response_persuasive">Persuasive</option>
                  <option value="response_pros_cons">Pros & Cons</option>
                  <option value="response_tweet">Tweet-Style</option>
                </select>
              </div>

              {/* Render the selected AI summary mode */}
              <div
                dangerouslySetInnerHTML={{
                  __html: formatAiSummary(
                    selectedBill.ai_summaries_enhanced?.[0]?.[selectedMode] ||
                      ""
                  ),
                }}
              />
            </div>

            {/* Bill history */}
            <div className="bill-history" style={{ marginTop: "15px" }}>
              <h4>History</h4>
              {selectedBill.history ? (
                <ul className="bill-history-list">
                  {selectedBill.history.split(";").map((entry, idx) => {
                    const [datePart, ...rest] = entry.trim().split(" - ");
                    return (
                      <li key={idx}>
                        <span className="bill-history-date">{datePart}</span>{" "}
                        <span className="bill-history-description">
                          {rest.join(" - ")}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <p>No history available.</p>
              )}
            </div>

            {/* Full Bill Link */}
            <a
              href={selectedBill.url}
              target="_blank"
              rel="noopener noreferrer"
              className="view-full-bill-link"
              style={{ display: "block", marginTop: "10px" }}
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
