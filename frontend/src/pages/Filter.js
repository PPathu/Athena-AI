import React from "react";
import { useNavigate } from "react-router-dom";

const Filter = () => {
  const navigate = useNavigate();

  return (
    <div className="filter-screen">
      <h2>Filter By</h2>
      <div>
        <h3>Document Type</h3>
        <input type="checkbox" checked /> PDF
        <input type="checkbox" checked /> Word
        <input type="checkbox" checked /> Excel
      </div>

      <div>
        <h3>Languages</h3>
        <input type="checkbox" checked /> English
        <input type="checkbox" checked /> Spanish
        <input type="checkbox" checked /> French
      </div>

      <footer>
        <button onClick={() => navigate("/")}>🏠</button>
        <button onClick={() => navigate("/search")}>🔙</button>
      </footer>
    </div>
  );
};

export default Filter;
