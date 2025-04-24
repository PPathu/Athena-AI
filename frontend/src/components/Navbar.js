import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import "../styles/styles.css";

const googleColors = [
  "var(--google-blue)",
  "var(--google-red)",
  "var(--google-yellow)",
  "var(--google-green)"
];

const Navbar = () => {
  const [menuOpen, setMenuOpen] = useState(false);
  const [activeColor, setActiveColor] = useState("var(--google-red)");

  const handleClick = () => {
    const randomColor = googleColors[Math.floor(Math.random() * googleColors.length)];
    setActiveColor(randomColor);
  };

  return (
    <nav className="navbar">
      <h1>Athena AI</h1>
      <button className="menu-toggle" onClick={() => setMenuOpen(!menuOpen)}>
        &#9776;
      </button>
      <ul className={menuOpen ? "nav-links open" : "nav-links"}>
        <li>
          <NavLink
            to="/"
            onClick={handleClick}
            className={({ isActive }) => isActive ? "active" : ""}
            style={({ isActive }) => isActive ? { backgroundColor: activeColor } : {}}
          >
            Home
          </NavLink>
        </li>
        <li>
          <NavLink
            to="/search"
            onClick={handleClick}
            className={({ isActive }) => isActive ? "active" : ""}
            style={({ isActive }) => isActive ? { backgroundColor: activeColor } : {}}
          >
            Bills
          </NavLink>
        </li>
      </ul>
    </nav>
  );
};

export default Navbar;