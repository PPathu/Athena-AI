import React, { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import supabase from "../utils/supabase";

const ViewBill = () => {
  const { bill_id } = useParams();
  const navigate = useNavigate();
  const [bill, setBill] = useState(null);

  useEffect(() => {
    const fetchBillDetails = async () => {
      const { data, error } = await supabase
        .from("enhanceddata")
        .select("*")
        .eq("bill_id", bill_id)
        .single();

      if (error) console.error("Error fetching bill details:", error);
      else setBill(data);
    };

    fetchBillDetails();
  }, [bill_id]);

  if (!bill) return <p>Loading bill details...</p>;

  return (
    <div>
      <h2>{bill.title || "Untitled Bill"}</h2>
      <p>{bill.description}</p>
      <p><strong>Status:</strong> {bill.status}</p>
      <p><strong>Last Action:</strong> {bill.last_action}</p>
      <button onClick={() => navigate("/search")}>Back to Search</button>
    </div>
  );
};

export default ViewBill;