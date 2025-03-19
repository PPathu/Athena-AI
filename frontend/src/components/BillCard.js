import React from "react";
import "../styles/BillCard.css"; 

const BillCard = ({ bill, onReadMore }) => {
  //shorten  bill description for card
  const shortDescription = bill.description
    ? bill.description.length > 100
      ? `${bill.description.substring(0, 100)}...`
      : bill.description
    : "No description available";

  //get an AI summary (shortened for the card)
  const aiSummary = bill.ai_summaries_enhanced?.[0]?.response;
  const shortAiSummary =
    aiSummary &&
    !aiSummary.includes("Since the title and description of the bill are unknown")
      ? aiSummary.slice(0, 120) + "..."
      : "No AI summary available";

  return (
    <div className="bill-card">
      <h3>{bill.title || "No Title"}</h3>
      <p className="bill-description">{shortDescription}</p>
      <p className="bill-summary">
        <strong>AI Summary:</strong> <br />
        {shortAiSummary}
      </p>
      <button onClick={() => onReadMore(bill)}>
        Read More
      </button>
    </div>
  );
};

export default BillCard;
