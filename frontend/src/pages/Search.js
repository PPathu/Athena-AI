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
  return sentences
    .map((sentence) => sentence.charAt(0).toUpperCase() + sentence.slice(1))
    .join(" ");
}

function formatAiSummary(rawText) {
  if (!rawText) return "No summary available.";
  const replaced = rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  return capitalizeSentences(replaced);
}

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
  const [selectedSummaryMode, setSelectedSummaryMode] = useState("response_simple");

  const billsPerPage = 6;

  const fetchBills = async () => {
    setLoading(true);
    setError("");
  
    try {
      let query = supabase
        .from("summarized_bills")
        .select("*")
        .not("response_simple", "is", null)
        .not("response_intermediate", "is", null)
        .not("response_persuasive", "is", null)
        .not("response_pros_cons", "is", null)
        .not("response_tweet", "is", null)
        .range((page - 1) * billsPerPage, page * billsPerPage - 1);
  
      if (searchTerm.trim()) {
        query = query.ilike("title", `%${searchTerm}%`);
      }
  
      const { data, error } = await query;
      if (error) throw error;
  
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
    setSelectedSummaryMode("response_simple");
  };

  const closeModal = () => {
    setSelectedBill(null);
  };

  const handleSummaryModeChange = (e) => {
    setSelectedSummaryMode(e.target.value);
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

      {loading && <div className="loader"></div>}
      {error && <p className="error-message">{error}</p>}

      <div className="bill-list">
        {bills.map((bill) => (
          <div key={bill.id} className="bill-card">
            <h3>{toTitleCase(bill.title)}</h3>
            <p className="bill-description">
              {getTwoSentenceSummary(bill.desc_response || bill.description)}
            </p>
            <button className="learn-more-btn" onClick={() => openModal(bill)}>
              Learn More
            </button>
          </div>
        ))}
      </div>

      <div className="pagination">
        {page > 1 && (
          <button onClick={() => setPage(page - 1)}>Previous</button>
        )}
        {bills.length === billsPerPage && (
          <button onClick={() => setPage(page + 1)}>Next</button>
        )}
      </div>

      {selectedBill && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={closeModal} className="close-btn">
              &times;
            </button>

            <h2>{toTitleCase(selectedBill.title)}</h2>

            {/* Description */}
            <div className="official-description" style={{ backgroundColor: "#eef4ff", padding: "10px", borderRadius: "6px" }}>
              <h4>Official Description</h4>
              <p>{capitalizeSentences(selectedBill.description)}</p>
            </div>

            {/* Status */}
            <div className="status-details" style={{ marginTop: "10px" }}>
              <p><strong>Bill Status:</strong> {selectedBill.status || "N/A"}</p>
              <p><strong>Last Action:</strong> {selectedBill.last_action || "N/A"}</p>
            </div>

            {/* AI Summary Modes */}
            <div className="ai-summary" style={{ marginTop: "15px" }}>
              <h4>AI Summarized Description</h4>
              <div style={{ marginBottom: "8px" }}>
                <select value={selectedSummaryMode} onChange={handleSummaryModeChange}>
                  <option value="response_simple">Simple & Clear</option>
                  <option value="response_intermediate">Straightforward</option>
                  <option value="response_persuasive">Persuasive</option>
                  <option value="response_pros_cons">Pros & Cons</option>
                  <option value="response_tweet">Tweet-Style</option>
                </select>
              </div>
              <div
                dangerouslySetInnerHTML={{
                  __html: formatAiSummary(
                    selectedBill[selectedSummaryMode] || "No summary available."
                  ),
                }}
              />
            </div>

            {/* Default AI Response */}
            <div className="default-ai-summary" style={{ marginTop: "15px" }}>
              <h4>Default AI Response</h4>
              <div
                dangerouslySetInnerHTML={{
                  __html: formatAiSummary(selectedBill.response || ""),
                }}
              />
            </div>

            {/* History */}
            <div className="bill-history" style={{ marginTop: "15px" }}>
              <h4>History</h4>
              {selectedBill.history ? (
                <ul className="bill-history-list">
                  {selectedBill.history.split(";").map((entry, idx) => {
                    const [datePart, ...rest] = entry.trim().split(" - ");
                    return (
                      <li key={idx}>
                        <span className="bill-history-date">{datePart}</span>{" "}
                        <span className="bill-history-description">{rest.join(" - ")}</span>
                      </li>
                    );
                  })}
                </ul>
              ) : (
                <p>No history available.</p>
              )}
            </div>

            {/* Link */}
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
