import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import supabase from "../utils/supabase";
import "../styles/styles.css";

const BillList = () => {
  const [bills, setBills] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchBills = async () => {
      const { data, error } = await supabase.from("enhanceddata").select("*");
      if (error) {
        console.error("Error fetching bills:", error);
      } else {
        setBills(data);
      }
    };

    fetchBills();
  }, []);

  return (
    <div>
      <h2>Bills</h2>
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
