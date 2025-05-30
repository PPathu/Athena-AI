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
  if (!rawText) return "No summary available.";
  return rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
}

/**
 * Return the first two sentences from some text, capitalizing them.
 */
function getTwoSentenceSummary(text) {
  if (!text) return "No description available.";
  const sentences = text.split(/(?<=[.!?])\s+/);
  return sentences.slice(0, 2).join(" ");
}

/**
 * Check if a bill has insufficient information
 */
function hasInsufficientInfo(bill) {
  // Check if desc_response explicitly mentions "not enough bill information"
  const descResponse = bill.ai_summaries_enhanced?.[0]?.desc_response || "";
  if (descResponse.toLowerCase().includes("not enough bill information")) {
    return true;
  }
  if (descResponse.toLowerCase().includes("more information is needed")) {
    return true;
  }
  if (descResponse.toLowerCase().includes("It doesn't say what")) {
    return true;
  }

  // Also check if description is empty or minimal
  const description = bill.description || "";
  if (!description.trim() || description.length < 10) {
    return true;
  }
  
  return false;
}

const Search = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [bills, setBills] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [selectedBill, setSelectedBill] = useState(null);
  // Two separate modes: one for the legislative description and one for the AI summary
  const [selectedDescriptionMode, setSelectedDescriptionMode] = useState("two_sentence");
  const [selectedSummaryMode, setSelectedSummaryMode] = useState("response_simple");
  const [userQuestion, setUserQuestion] = useState("");
  const [aiAnswer, setAiAnswer] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  
  const billsPerPage = 6;

  /**
   * Fetch bills from Supabase with legislative and summarized descriptions
   */
  const fetchBills = async () => {
    setLoading(true);
    setError("");

    try {
      let query = supabase
        .from("enhanceddata")
        .select(
          `*, 
          ai_summaries_enhanced:ai_summaries_enhanced(
            response, 
            desc_response, 
            response_simple, 
            response_intermediate, 
            response_persuasive, 
            response_pros_cons, 
            response_tweet
          )`
        );

      // Search in both title and description if searchTerm is provided
      if (searchTerm.trim()) {
        query = query.or(`title.ilike.%${searchTerm}%,description.ilike.%${searchTerm}%`);
      }

      // Fetch more bills than we need to account for filtering
      // Fetch 3x the number to ensure we have enough after filtering
      const { data: unfilteredData, error } = await query
        .range((page - 1) * billsPerPage * 3, (page * billsPerPage * 3) - 1);
        
      if (error) throw error;

      // Filter out bills with insufficient information
      const filteredData = unfilteredData.filter(bill => !hasInsufficientInfo(bill));

      // Remove duplicate bills (by title)
      const uniqueBills = [];
      const titleSet = new Set();
      
      for (const bill of filteredData) {
        const title = bill.title?.toLowerCase();
        if (title && !titleSet.has(title)) {
          titleSet.add(title);
          uniqueBills.push(bill);
        }
      }

      // Take only the bills we need for this page
      const paginatedBills = uniqueBills.slice(0, billsPerPage);
      
      setBills(paginatedBills);
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

  useEffect(() => {
    // Reset to page 1 when search term changes
    setPage(1);
  }, [searchTerm]);

  /** 
   * Open the modal with details for a chosen bill and reset modes 
   */
  const openModal = (bill) => {
    // Double-check that this bill has sufficient information before showing modal
    if (hasInsufficientInfo(bill)) {
      setError("This bill doesn't have enough information to display.");
      return;
    }
    
    setSelectedBill(bill);
    setSelectedDescriptionMode("two_sentence");
    setSelectedSummaryMode("response_simple");
  };

  const closeModal = () => {
    setSelectedBill(null);
  };

  const handleDescriptionModeChange = (e) => {
    setSelectedDescriptionMode(e.target.value);
  };

  const handleSummaryModeChange = (e) => {
    setSelectedSummaryMode(e.target.value);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchBills();
  };

  const askAiAboutBill = async () => {
    if (!userQuestion.trim()) return;
  
    setAiLoading(true);
    setAiAnswer("");
  
    try {
      const response = await fetch("http://127.0.0.1:5000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          bill_id: selectedBill.bill_id,
          question: userQuestion,
        }),
      });
  
      const text = await response.text(); // Raw response for debugging
  
      if (!response.ok) {
        throw new Error(`HTTP ${response.status} – ${text}`);
      }
  
      const data = text ? JSON.parse(text) : {};
      console.log("AI Response:", data);
  
      if (typeof data.answer === "string") {
        setAiAnswer(data.answer);
      } else {
        setAiAnswer("AI did not return a valid answer.");
      }
    } catch (error) {
      console.error("Error asking AI:", error);
      setAiAnswer("Failed to get an answer. " + error.message);
    } finally {
      setAiLoading(false);
    }
  };
  
  return (
    <div className="search-container">

      {/* Search bar */}

      <img
        src="/athena-logo.png"  
        className="athena-logo"
      />

      <div className="search-bar">
        <form onSubmit={handleSearch}>
          <input
            type="text"
            placeholder="Search bills by title or description..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <button type="submit">Search</button>
        </form>
      </div>

      {/* Loading / Error */}
      {loading && <p className="loading-text">Loading bills...</p>}
      {error && <p className="error-message">{error}</p>}

      {/* Bill list: each card shows short text */}
      <div className="bill-list">
        {bills.length > 0 ? (
          bills.map((bill) => {
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
            {/* Close button */}
            <button onClick={closeModal} className="close-btn">
              &times;
            </button>

            {/* Bill title */}
            <h2>{toTitleCase(selectedBill.title)}</h2>

            {/* Legislative Description Section */}
            <div className="description-section" style={{ background: "#f0f4f8", padding: "10px", borderRadius: "4px", marginBottom: "15px" }}>
              <h4>Legislative Description</h4>
              {/* Description mode selection */}
              <div style={{ marginBottom: "8px" }}>
                <select 
                  value={selectedDescriptionMode} 
                  onChange={handleDescriptionModeChange}
                >
                  <option value="two_sentence">Two-Sentence Summary</option>
                  <option value="full_description">Full Legislative Description</option>
                </select>
              </div>
              {/* Render description based on selected mode */}
              <p>
                {selectedDescriptionMode === 'two_sentence' 
                  ? getTwoSentenceSummary(
                      selectedBill.ai_summaries_enhanced?.[0]?.desc_response || 
                      selectedBill.description || 
                      "No description available."
                    )
                  : (
                      selectedBill.description || 
                      "No full legislative description available."
                    )
                }
              </p>
            </div>

            {/* Bill Status Section */}
            <div className="status-details" style={{ marginTop: "10px", marginBottom: "15px" }}>
              <p>
                <strong>Bill Status:</strong> {selectedBill.status || "N/A"}
              </p>
              <p>
                <strong>Last Action:</strong> {selectedBill.last_action || "N/A"}
              </p>
            </div>

            {/* AI Summarized Description Section */}
            <div className="ai-summary" style={{ marginTop: "15px" }}>
              <h4>AI Summarized Description</h4>
              {/* Summary mode selection */}
              <div style={{ marginBottom: "8px" }}>
                <select value={selectedSummaryMode} onChange={handleSummaryModeChange}>
                  <option value="response_simple">Simple</option>
                  <option value="response_intermediate">Informed</option>
                  <option value="response_persuasive">Why It Matters</option>
                  <option value="response_pros_cons">Pros & Cons</option>
                  <option value="response_tweet">Tweet-Style</option>
                </select>
              </div>
              {/* Render the selected AI summary mode */}
              <div
                dangerouslySetInnerHTML={{
                  __html: formatAiSummary(
                    selectedBill.ai_summaries_enhanced?.[0]?.[selectedSummaryMode] ||
                      "No AI summary available."
                  ),
                }}
              />
            </div>

            {/* Bill History Section */}
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

            {/* Bill Sponsors Section */}
           <div className="bill-sponsors" style={{ marginTop: "15px" }}>
             <h4>Sponsors</h4>
             {selectedBill.sponsors ? (() => {
               let sponsorList;
               try {
                 sponsorList = JSON.parse(selectedBill.sponsors);
               } catch (e) {
                 console.error("Failed to parse sponsors JSON:", e);
                 sponsorList = [];
               }
 
               return sponsorList.length > 0 ? (
                 sponsorList.map((sponsor, idx) => (
                   <div key={idx} style={{ marginBottom: "10px" }}>
                     <strong>{sponsor.name}</strong> ({sponsor.role}, {sponsor.party}-{sponsor.district})
                     {sponsor.ballotpedia && (
                       <span>
                         {" "}
                         - <a href={`https://ballotpedia.org/${sponsor.ballotpedia}`} target="_blank" rel="noreferrer">Ballotpedia</a>
                       </span>
                     )}
                   </div>
                 ))
               ) : (
                 <p>No sponsors listed.</p>
               );
             })() : (
               <p>No sponsors listed.</p>
             )}
           </div>
           
            {/* Ask AI About This Bill */}
            <div className="ask-ai-section" style={{ marginTop: "20px" }}>
              <h4>Ask AI About This Bill</h4>

              <div className="preset-buttons" style={{ marginBottom: "10px" }}>
                {[
                  "What does this bill aim to do?",
                  "Who supports or opposes this bill?",
                  "What stage is this bill in the legislative process?"
                ].map((preset, idx) => (
                  <button
                    key={idx}
                    className="preset-button"
                    onClick={() => {
                      setUserQuestion(preset);
                      setAiAnswer("");
                      askAiAboutBill();
                    }}
                  >
                    {preset}
                  </button>
                ))}
              </div>

              <textarea
                rows="3"
                placeholder="Type your question here..."
                value={userQuestion}
                onChange={(e) => setUserQuestion(e.target.value)}
                style={{ width: "100%", padding: "8px" }}
              />
              <button
                onClick={askAiAboutBill}
                disabled={aiLoading}
                style={{ marginTop: "10px" }}
              >
                {aiLoading ? "Thinking..." : "Ask"}
              </button>

              {aiAnswer && (
                <div
                  className="ai-answer"
                  style={{
                    marginTop: "15px",
                    backgroundColor: "#f9f9f9",
                    padding: "10px",
                    borderRadius: "4px",
                  }}
                  dangerouslySetInnerHTML={{ __html: formatAiSummary(aiAnswer) }}
                />
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




// import React, { useState, useEffect } from "react";
// import supabase from "../utils/supabase";
// import "../styles/styles.css";

// /** 
//  * Convert a string to Title Case 
//  */
// function toTitleCase(str) {
//   if (!str) return "";
//   return str.replace(/\w\S*/g, (txt) => {
//     return txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase();
//   });
// }

// /** 
//  * Capitalize the first letter of each sentence. 
//  */
// function capitalizeSentences(text) {
//   if (!text) return "";
//   const sentences = text.split(/(?<=[.!?])\s+/);
//   return sentences
//     .map(
//       (sentence) =>
//         sentence.charAt(0).toUpperCase() + sentence.slice(1).toLowerCase()
//     )
//     .join(" ");
// }

// /** 
//  * Convert simple Markdown-like bold (**word**) into HTML <strong> 
//  * and then capitalize sentences. 
//  */
// function formatAiSummary(rawText) {
//   if (!rawText) return "No summary available.";
//   return rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
// }

// /**
//  * Return the first two sentences from some text, capitalizing them.
//  */
// function getTwoSentenceSummary(text) {
//   if (!text) return "No description available.";
//   const sentences = text.split(/(?<=[.!?])\s+/);
//   return sentences.slice(0, 2).join(" ");
// }

// const Search = () => {
//   const [searchTerm, setSearchTerm] = useState("");
//   const [bills, setBills] = useState([]);
//   const [loading, setLoading] = useState(false);
//   const [error, setError] = useState("");
//   const [page, setPage] = useState(1);
//   const [selectedBill, setSelectedBill] = useState(null);
//   // Two separate modes: one for the legislative description and one for the AI summary
//   const [selectedDescriptionMode, setSelectedDescriptionMode] = useState("two_sentence");
//   const [selectedSummaryMode, setSelectedSummaryMode] = useState("response_simple");
//   const [userQuestion, setUserQuestion] = useState("");
//   const [aiAnswer, setAiAnswer] = useState("");
//   const [aiLoading, setAiLoading] = useState(false);
  
//   const billsPerPage = 6;

//   /**
//    * Fetch bills from Supabase with legislative and summarized descriptions
//    */
//   const fetchBills = async () => {
//     setLoading(true);
//     setError("");

//     try {
//       let query = supabase
//         .from("enhanceddata")
//         .select(
//           `*, 
//           ai_summaries_enhanced:ai_summaries_enhanced(
//             response, 
//             desc_response, 
//             response_simple, 
//             response_intermediate, 
//             response_persuasive, 
//             response_pros_cons, 
//             response_tweet
//           )`
//         )
//         .range((page - 1) * billsPerPage, page * billsPerPage - 1);

//        if (searchTerm.trim()) {
//          query = query.ilike("title", `%${searchTerm}%`);
//       }
//       const { data, error } = await query;
//       if (error) throw error;

//       setBills(data);
//     } catch (err) {
//       console.error("Supabase fetch error:", err);
//       setError("Failed to fetch bills. Please try again.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     fetchBills();
//   }, [page]);

//   /** 
//    * Open the modal with details for a chosen bill and reset modes 
//    */
//   const openModal = (bill) => {
//     setSelectedBill(bill);
//     setSelectedDescriptionMode("two_sentence");
//     setSelectedSummaryMode("response_simple");
//   };

//   const closeModal = () => {
//     setSelectedBill(null);
//   };

//   const handleDescriptionModeChange = (e) => {
//     setSelectedDescriptionMode(e.target.value);
//   };

//   const handleSummaryModeChange = (e) => {
//     setSelectedSummaryMode(e.target.value);
//   };

//   const askAiAboutBill = async () => {
//     if (!userQuestion.trim()) return;
  
//     setAiLoading(true);
//     setAiAnswer("");
  
//     try {
//       const response = await fetch("http://127.0.0.1:5000/api/chat", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({
//           bill_id: selectedBill.bill_id,
//           question: userQuestion,
//         }),
//       });


  
//       const text = await response.text(); // Raw response for debugging
  
//       if (!response.ok) {
//         throw new Error(`HTTP ${response.status} – ${text}`);
//       }
  
//       const data = text ? JSON.parse(text) : {};
//       console.log("AI Response:", data);
  
//       if (typeof data.answer === "string") {
//         setAiAnswer(data.answer);
//       } else {
//         setAiAnswer("AI did not return a valid answer.");
//       }
//     } catch (error) {
//       console.error("Error asking AI:", error);
//       setAiAnswer("Failed to get an answer. " + error.message);
//     } finally {
//       setAiLoading(false);
//     }
//   };
  
//   return (
//     <div className="search-container">
//       <h2>Search Bills</h2>

//       {/* Search bar */}
//       <div className="search-bar">
//         <input
//           type="text"
//           placeholder="Search bills..."
//           value={searchTerm}
//           onChange={(e) => setSearchTerm(e.target.value)}
//         />
//         <button onClick={fetchBills}>Search</button>
//       </div>

//       {/* Loading / Error */}
//       {loading && <p className="loading-text">Loading bills...</p>}
//       {error && <p className="error-message">{error}</p>}

//       {/* Bill list: each card shows short text */}
//       <div className="bill-list">
//         {bills.length > 0 ? (
//           bills.map((bill) => {
//             const shortDesc =
//               bill.ai_summaries_enhanced?.[0]?.desc_response ||
//               bill.description ||
//               "No description available.";

//             return (
//               <div key={bill.id} className="bill-card">
//                 <h3>{(bill.title)}</h3>
//                 <p className="bill-description">
//                   {getTwoSentenceSummary(shortDesc)}
//                 </p>
//                 <button className="learn-more-btn" onClick={() => openModal(bill)}>
//                   Learn More
//                 </button>
//               </div>
//             );
//           })
//         ) : (
//           <p className="no-results">No matching bills found.</p>
//         )}
//       </div>

//       {/* Pagination controls */}
//       <div className="pagination" style={{ marginBottom: "40px" }}>
//         {page > 1 && (
//           <button onClick={() => setPage(page - 1)}>Previous</button>
//         )}
//         {bills.length === billsPerPage && (
//           <button onClick={() => setPage(page + 1)}>Next</button>
//         )}
//       </div>

//       {/* Modal for expanded details */}
//       {selectedBill && (
//         <div className="modal-overlay">
//           <div className="modal-content">
//             {/* Close button */}
//             <button onClick={closeModal} className="close-btn">
//               &times;
//             </button>

//             {/* Bill title */}
//             <h2>{toTitleCase(selectedBill.title)}</h2>

//             {/* Legislative Description Section */}
//             <div className="description-section" style={{ background: "#f0f4f8", padding: "10px", borderRadius: "4px", marginBottom: "15px" }}>
//               <h4>Legislative Description</h4>
//               {/* Description mode selection */}
//               <div style={{ marginBottom: "8px" }}>
//                 <select 
//                   value={selectedDescriptionMode} 
//                   onChange={handleDescriptionModeChange}
//                 >
//                   <option value="two_sentence">Two-Sentence Summary</option>
//                   <option value="full_description">Full Legislative Description</option>
//                 </select>
//               </div>
//               {/* Render description based on selected mode */}
//               <p>
//                 {selectedDescriptionMode === 'two_sentence' 
//                   ? getTwoSentenceSummary(
//                       selectedBill.ai_summaries_enhanced?.[0]?.desc_response || 
//                       selectedBill.description || 
//                       "No description available."
//                     )
//                   : (
//                       selectedBill.description || 
//                       "No full legislative description available."
//                     )
//                 }
//               </p>
//             </div>

//             {/* Bill Status Section */}
//             <div className="status-details" style={{ marginTop: "10px", marginBottom: "15px" }}>
//               <p>
//                 <strong>Bill Status:</strong> {selectedBill.status || "N/A"}
//               </p>
//               <p>
//                 <strong>Last Action:</strong> {selectedBill.last_action || "N/A"}
//               </p>
//             </div>

//             {/* AI Summarized Description Section */}
//             <div className="ai-summary" style={{ marginTop: "15px" }}>
//               <h4>AI Summarized Description</h4>
//               {/* Summary mode selection */}
//               <div style={{ marginBottom: "8px" }}>
//                 <select value={selectedSummaryMode} onChange={handleSummaryModeChange}>
//                   <option value="response_simple">Simple & Clear</option>
//                   <option value="response_intermediate">Straightforward</option>
//                   <option value="response_persuasive">Persuasive</option>
//                   <option value="response_pros_cons">Pros & Cons</option>
//                   <option value="response_tweet">Tweet-Style</option>
//                 </select>
//               </div>
//               {/* Render the selected AI summary mode */}
//               <div
//                 dangerouslySetInnerHTML={{
//                   __html: formatAiSummary(
//                     selectedBill.ai_summaries_enhanced?.[0]?.[selectedSummaryMode] ||
//                       "No AI summary available."
//                   ),
//                 }}
//               />
//             </div>


//             {/* Default AI Response Section */}
//             {/* <div className="default-ai-summary" style={{ marginTop: "15px" }}>
//               <h4>Default AI Response</h4>
//               <div
//                 dangerouslySetInnerHTML={{
//                   __html: formatAiSummary(
//                     selectedBill.ai_summaries_enhanced?.[0]?.response ||
//                       "No default response available."
//                   ),
//                 }}
//               />
//             </div> */}


//             {/* Bill History Section */}
//             <div className="bill-history" style={{ marginTop: "15px" }}>
//               <h4>History</h4>
//               {selectedBill.history ? (
//                 <ul className="bill-history-list">
//                   {selectedBill.history.split(";").map((entry, idx) => {
//                     const [datePart, ...rest] = entry.trim().split(" - ");
//                     return (
//                       <li key={idx}>
//                         <span className="bill-history-date">{datePart}</span>{" "}
//                         <span className="bill-history-description">
//                           {rest.join(" - ")}
//                         </span>
//                       </li>
//                     );
//                   })}
//                 </ul>
//               ) : (
//                 <p>No history available.</p>
//               )}
//             </div>

//             {/* Bill Sponsors Section */}
//            <div className="bill-sponsors" style={{ marginTop: "15px" }}>
//              <h4>Sponsors</h4>
//              {selectedBill.sponsors ? (() => {
//                let sponsorList;
//                try {
//                  sponsorList = JSON.parse(selectedBill.sponsors);
//                } catch (e) {
//                  console.error("Failed to parse sponsors JSON:", e);
//                  sponsorList = [];
//                }
 
//                return sponsorList.length > 0 ? (
//                  sponsorList.map((sponsor, idx) => (
//                    <div key={idx} style={{ marginBottom: "10px" }}>
//                      <strong>{sponsor.name}</strong> ({sponsor.role}, {sponsor.party}-{sponsor.district})
//                      {sponsor.ballotpedia && (
//                        <span>
//                          {" "}
//                          - <a href={`https://ballotpedia.org/${sponsor.ballotpedia}`} target="_blank" rel="noreferrer">Ballotpedia</a>
//                        </span>
//                      )}
//                    </div>
//                  ))
//                ) : (
//                  <p>No sponsors listed.</p>
//                );
//              })() : (
//                <p>No sponsors listed.</p>
//              )}
//            </div>

//             {/* Ask AI About This Bill */}
//             <div className="ask-ai-section" style={{ marginTop: "20px" }}>
//               <h4>Ask AI About This Bill</h4>

//               <div className="preset-buttons" style={{ marginBottom: "10px" }}>
//                 {[
//                   "What does this bill aim to do?",
//                   "Who supports or opposes this bill?",
//                   "What stage is this bill in the legislative process?"
//                 ].map((preset, idx) => (
//                   <button
//                     key={idx}
//                     className="preset-button"
//                     onClick={() => {
//                       setUserQuestion(preset);
//                       askAiAboutBill();
//                     }}
//                   >
//                     {preset}
//                   </button>
//                 ))}
//               </div>

//               <textarea
//                 rows="3"
//                 placeholder="Type your question here..."
//                 value={userQuestion}
//                 onChange={(e) => setUserQuestion(e.target.value)}
//                 style={{ width: "100%", padding: "8px" }}
//               />
//               <button
//                 onClick={askAiAboutBill}
//                 disabled={aiLoading}
//                 style={{ marginTop: "10px" }}
//               >
//                 {aiLoading ? "Thinking..." : "Ask"}
//               </button>

//               {aiAnswer && (
//                 <div
//                   className="ai-answer"
//                   style={{
//                     marginTop: "15px",
//                     backgroundColor: "#f9f9f9",
//                     padding: "10px",
//                     borderRadius: "4px",
//                   }}
//                   dangerouslySetInnerHTML={{ __html: formatAiSummary(aiAnswer) }}
//                 />
//               )}
//             </div>

//             {/* Full Bill Link */}
//             <a
//               href={selectedBill.url}
//               target="_blank"
//               rel="noopener noreferrer"
//               className="view-full-bill-link"
//               style={{ display: "block", marginTop: "10px" }}
//             >
//               View Full Bill
//             </a>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// };

// export default Search;