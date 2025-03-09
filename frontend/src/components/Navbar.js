import React from "react";
import { NavLink } from "react-router-dom";
import "../styles/Navbar.css";

const Navbar = () => {
  return (
    <nav className="navbar">
      <h1>Athena AI</h1>
      <ul>
        <li><NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>Home</NavLink></li>
        <li><NavLink to="/search" className={({ isActive }) => isActive ? "active" : ""}>Search</NavLink></li>
        <li><NavLink to="/stats" className={({ isActive }) => isActive ? "active" : ""}>Stats</NavLink></li>
      </ul>
    </nav>
  );
};

export default Navbar;
