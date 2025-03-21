import React, { useState, useEffect } from "react";
import supabase from "../utils/supabase";
import "../styles/styles.css";

// helper function to convert text to title case
function toTitleCase(str) {
  if (!str) return "";
  return str.replace(/\w\S*/g, (txt) => {
    return txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase();
  });
}

// capitalize each sentence
function capitalizeSentences(text) {
  if (!text) return "";
  const sentences = text.split(/(?<=[.!?])\s+/);
  return sentences.map(sentence => sentence.charAt(0).toUpperCase() + sentence.slice(1)).join(" ");
}

// format ai summary (simple formatting)
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
  const [selectedMode, setSelectedMode] = useState("response_simple");
  const billsPerPage = 6;

  // helper: extract the first two sentences from a bill description
  const getTwoSentenceSummary = (text) => {
    if (!text) return null;
    const capitalized = capitalizeSentences(text);
    const sentences = capitalized.split(/(?<=[.!?])\s+/);
    return sentences.slice(0, 2).join(" ");
  };

  // fetch bills from Supabase (including all AI summary columns)
  const fetchBills = async () => {
    setLoading(true);
    setError("");

    try {
      console.log("searching for:", searchTerm);

      let query = supabase
        .from("enhanceddata")
        .select("*, ai_summaries_enhanced:ai_summaries_enhanced(desc_response, response)") // Fetch both desc_response and response
        .range((page - 1) * billsPerPage, page * billsPerPage - 1);

      if (searchTerm.trim()) {
        query = query.ilike("title", `%${searchTerm}%`);
      }

      const { data, error } = await query;
      if (error) throw error;

      console.log("bills from supabase:", data);
      setBills(data);
    } catch (err) {
      console.error("supabase fetch error:", err);
      setError("Failed to fetch bills. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBills();
  }, [page]);

  // open modal for selected bill
  const openModal = (bill) => {
    setSelectedBill(bill);
    setSelectedMode("response_simple"); // default mode when opening modal
  };

  // close modal
  const closeModal = () => {
    setSelectedBill(null);
  };

  // handle mode selection change
  const handleModeChange = (e) => {
    setSelectedMode(e.target.value);
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
      const aiSummary = bill.ai_summaries_enhanced?.[0]?.desc_response 
                       || bill.ai_summaries_enhanced?.desc_response;
      const finalDescription = aiSummary 
        ? aiSummary 
        : bill.description 
          ? bill.description 
          : "No description available";

      return (
        <div key={bill.id} className="bill-card">
          <h3>{toTitleCase(bill.title)}</h3>
          <p className="bill-description">
            {getTwoSentenceSummary(finalDescription)}
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
      <div className="pagination">
        {page > 1 && (
          <button onClick={() => setPage(page - 1)}>Previous</button>
        )}
        {bills.length === billsPerPage && (
          <button onClick={() => setPage(page + 1)}>Next</button>
        )}
      </div>

      {/* Modal for detailed bill view */}
      {selectedBill && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={closeModal} className="close-btn">
              &times;
            </button>
            <h2>{toTitleCase(selectedBill.title)}</h2>
            <div className="official-description">
              <h4>Official Description</h4>
              <p>{capitalizeSentences(selectedBill.description)}</p>
            </div>
            <div className="status-details">
              <p>
                <strong>Bill Status:</strong> {selectedBill.status || "N/A"}
              </p>
              <p>
                <strong>Last Action:</strong> {selectedBill.last_action || "N/A"}
              </p>
            </div>
            <div className="ai-summary">
              <h4>AI Summary</h4>
              <div>
                <select value={selectedMode} onChange={handleModeChange}>
                  <option value="response_simple">Simple & Clear</option>
                  <option value="response_intermediate">Straightforward</option>
                  <option value="response_persuasive">Persuasive</option>
                  <option value="response_pros_cons">Pros & Cons</option>
                  <option value="response_tweet">Tweet-Style</option>
                </select>
              </div>
              <div
                dangerouslySetInnerHTML={{
                  __html:
                    selectedBill.ai_summaries_enhanced?.[0]?.[selectedMode] ||
                    "No AI summary available",
                }}
              />
            </div>
            <div className="bill-history">
              <h4>History</h4>
              <ul className="bill-history-list">
                {selectedBill.history ? (
                  selectedBill.history.split(";").map((entry, idx) => {
                    const [datePart, ...rest] = entry.trim().split(" - ");
                    return (
                      <li key={idx}>
                        <span className="bill-history-date">{datePart}</span>{" "}
                        <span className="bill-history-description">
                          {rest.join(" - ")}
                        </span>
                      </li>
                    );
                  })
                ) : (
                  <p>No history available.</p>
                )}
              </ul>
            </div>
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
