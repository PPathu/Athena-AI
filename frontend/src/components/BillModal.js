import React from "react";
import "../styles/styles.css";

const BillModal = ({ bill, onClose }) => {
  if (!bill) return null;

  //get AI summary
  const aiSummary =
    bill.ai_summaries_enhanced?.[0]?.response ||
    "No AI summary available";


  const amendments = bill.amendments || []; // array of amendment objects
  const sponsors = bill.sponsors || []; // array of sponsor objects
  const officialDescription = bill.description || "No description available";

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        {/* Close Button */}
        <button className="close-modal-btn" onClick={onClose}>
          &times;
        </button>

        {/* bill title */}
        <h2 className="bill-title">
          {bill.title || "Untitled Bill"}
        </h2>

        {/* official description */}
        <div className="bill-section">
          <h3>Official Description</h3>
          <p className="bill-official-desc">{officialDescription}</p>
        </div>

        {/* AI summary */}
        <div className="bill-section">
          <h3>AI Summary</h3>
          <p className="bill-ai-summary">{aiSummary}</p>
        </div>

        {/* bill status */}
        <div className="bill-section">
          <h3>Bill Status</h3>
          <p>
            <strong>Status:</strong> {bill.status || "Unknown"}
          </p>
          <p>
            <strong>Last Action:</strong>{" "}
            {bill.last_action || "N/A"}
          </p>
          <p>
            <strong>History:</strong>{" "}
            {bill.history || "No history provided"}
          </p>
        </div>

        {/* amendments */}
        {amendments.length > 0 && (
          <div className="bill-section">
            <h3>Relevant Amendments / Summaries</h3>
            <ul>
              {amendments.map((amend, index) => (
                <li key={index}>
                  <strong>{amend.title}</strong>
                  <p>{amend.description}</p>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* sponsors */}
        {sponsors.length > 0 && (
          <div className="bill-section sponsors">
            <h3>Sponsors</h3>
            <table>
              <thead>
                <tr>
                  <th>Democrat</th>
                  <th>Republican</th>
                </tr>
              </thead>
              
              <tbody>
                {sponsors.map((s, i) => (
                  <tr key={i}>
                    <td>{s.democratName || ""}</td>
                    <td>{s.republicanName || ""}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* link to full bill */}
        {bill.url && (
          <div className="bill-section">
            <a
              href={bill.url}
              target="_blank"
              rel="noopener noreferrer"
              className="view-full-bill-link"
            >
              Official Text
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default BillModal;