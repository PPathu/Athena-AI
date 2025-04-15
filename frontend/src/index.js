import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import Search from "./pages/Search";
import ChatBot from "./pages/Chatbot";
import "./styles/styles.css"; 

ReactDOM.render(
  <Router>
    <Navbar />
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/search" element={<Search />} />
      <Route path="/chatbot" element={<ChatBot />} />
    </Routes>
  </Router>,
  document.getElementById("root")
);
