import React, { useEffect, useState } from "react";
import supabase from "../utils/supabase";  // ✅ Correct
import { Bar } from "react-chartjs-2";
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from "chart.js";

const ChatBot = () => {
  return (
    <div style={{ textAlign: "center", padding: "20px" }}>
      <h2>Legislative ChatBot</h2>
      <p>Coming soon...</p>
    </div>
  );
};

export default ChatBot;
