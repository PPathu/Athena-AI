import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/styles.css";

const BillList = () => {
  const [bills, setBills] = useState([]);
  const navigate = useNavigate();

  
  useEffect(() => {
    fetch("http://localhost:5000/bills")
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to fetch bills");
      }
      return response.json();

    })
    .then(data => {
      setBills(data);
    }).catch(error => {
      console.error("Error fetching bills:", error);
    });
  }, []);

  return (
    <div>
      <h2>📜 Bills</h2>
      {bills.length > 0 ? (
        bills.map((bill) => (
          <div key={bill.bill_id} className="bill-card">
            <h3>{bill.title || "Untitled Bill"}</h3>
            <p>{bill.description}</p>
            <button onClick={() => navigate(`/view-bill/${bill.bill_id}`)}>
              View Details
            </button>
          </div>
        ))
      ) : (
        <p>Loading bills...</p>
      )}
    </div>
  );
};

export default BillList;
