import React, { useState } from "react";
import supabase from "../utils/supabase";
import "../styles/styles.css";

function capitalizeSentences(text) {
  if (!text) return "";
  const sentences = text.split(/(?<=[.!?])\s+/);
  return sentences
    .map((sentence) =>
      sentence.charAt(0).toUpperCase() + sentence.slice(1).toLowerCase()
    )
    .join(" ");
}

function formatAiSummary(rawText) {
  if (!rawText) return "No summary available.";
  const replaced = rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  return capitalizeSentences(replaced);
}

const Home = () => {
  const [randomBill, setRandomBill] = useState(null);

  const handleRandomBill = async () => {
    const { data, error } = await supabase
      .from("enhanceddata")
      .select(
        `*, 
        ai_summaries_enhanced:ai_summaries_enhanced(
          response_simple
        )`
      )
      .not("ai_summaries_enhanced.response_simple", "is", null); // 👈 only get bills with a summary
  
    if (error) {
      console.error("Error fetching bills:", error);
      return;
    }
  
    const filtered = data.filter(
      (bill) => bill.ai_summaries_enhanced?.[0]?.response_simple
    );
  
    if (filtered.length > 0) {
      const randomIndex = Math.floor(Math.random() * filtered.length);
      const bill = filtered[randomIndex];
      setRandomBill(bill);
    } else {
      console.warn("No bills found with a summary.");
    }
  };
  

  const closeModal = () => {
    setRandomBill(null);
  };

  return (
    <div style={{ textAlign: "center", padding: "50px" }}>
      <h1>Athena AI</h1>
      <p>Legislation just got easier.</p>
      <button
        onClick={handleRandomBill}
        className="rainbow-button"
        style={{ marginTop: "20px", padding: "10px 20px", fontSize: "16px" }}
      >
        Bill of the Day
      </button>

      {randomBill && (
        <div className="modal-overlay">
          <div className="modal-content">
            <button onClick={closeModal} className="close-btn">&times;</button>

            <h2>{randomBill.title || "Untitled Bill"}</h2>

            <div style={{ marginTop: "10px", marginBottom: "15px" }}>
              <p><strong>Status:</strong> {randomBill.status || "N/A"}</p>
              <p><strong>Last Action:</strong> {randomBill.last_action || "N/A"}</p>
            </div>

            <div className="ai-summary" style={{ marginTop: "15px" }}>
              <h4>AI Summarized Description</h4>
              <div
                dangerouslySetInnerHTML={{
                  __html: formatAiSummary(
                    randomBill.ai_summaries_enhanced?.[0]?.response_simple ||
                    "No AI summary available."
                  )
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;
