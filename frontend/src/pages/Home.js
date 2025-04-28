import React, { useState } from "react";
import supabase from "../utils/supabase";

import "../styles/styles.css";

/* ─────────── Helper utilities ─────────── */
function capitalizeSentences(text) {
  if (!text) return "";
  return text
    .split(/(?<=[.!?])\s+/)
    .map(
      (sentence) =>
        sentence.charAt(0).toUpperCase() + sentence.slice(1).toLowerCase()
    )
    .join(" ");
}

function formatAiSummary(rawText) {
  if (!rawText) return "No summary available.";
  // Markdown bold (**text**) ➜ <strong>
  return capitalizeSentences(rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"));
}

/* ───────────── Home component ───────────── */
const Home = () => {
  const [randomBill, setRandomBill] = useState(null);

  /* Grab a random bill that has a “simple” AI summary */
  const handleRandomBill = async () => {
    const { data, error } = await supabase
      .from("enhanceddata")
      .select(`*, ai_summaries_enhanced:ai_summaries_enhanced(response_simple)`)
      .not("ai_summaries_enhanced.response_simple", "is", null);

    if (error) {
      console.error("Error fetching bills:", error);
      return;
    }

    const filtered = data.filter(
      (bill) => bill.ai_summaries_enhanced?.[0]?.response_simple
    );
    if (!filtered.length) {
      console.warn("No bills found with a summary.");
      return;
    }

    const randomIndex = Math.floor(Math.random() * filtered.length);
    setRandomBill(filtered[randomIndex]);
  };

  const closeModal = () => setRandomBill(null);

  /* PUBLIC_URL ensures the path still works when you deploy under a sub-directory */
  const logoUrl = `${process.env.PUBLIC_URL}/athena-logo.png`;

  /* ────────────── Render ────────────── */
  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(to bottom right, #eef2f7, #ffffff)",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        padding: "120px 20px 40px",
        position: "relative",
      }}
    >
      {/* ◉ Logo */}
            <img
        src="/athena-logo.png"      // nothing else
        alt="Athena AI logo"
        className="athena-logo"
      />


      {/* Hero heading */}
      <h1
        style={{
          fontSize: "4rem",
          fontWeight: "bold",
          textAlign: "center",
          background:
            "linear-gradient(270deg, #4285F4, #EA4335, #FBBC05, #34A853, #4285F4)",
          backgroundSize: "800% 800%",
          WebkitBackgroundClip: "text",
          WebkitTextFillColor: "transparent",
          animation: "rainbowTextMove 6s linear infinite",
          marginBottom: "20px",
        }}
      >
        Democracy, Simplified
      </h1>

      {/* Sub-heading */}
      <p
        style={{
          fontSize: "1.3rem",
          color: "#5f6368",
          textAlign: "center",
          maxWidth: "700px",
          marginBottom: "40px",
        }}
      >
        Making legislation accessible and understandable for everyone with
        AI-powered insights and analysis.
      </p>

      {/* CTA button */}
      <button
        onClick={handleRandomBill}
        className="premium-rainbow-button"
        style={{ marginBottom: "50px" }}
      >
        Show Me a Random Bill
      </button>

      {/* ───────── Modal ───────── */}
      {randomBill && (
        <div className="modal-overlay">
          <div className="modal-content" style={{ padding: "30px", maxWidth: "700px" }}>
            <button onClick={closeModal} className="close-btn">
              &times;
            </button>

            <h2
              style={{
                textAlign: "center",
                fontSize: "1.75rem",
                marginBottom: "20px",
              }}
            >
              {randomBill.title || "Untitled Bill"}
            </h2>

            {/* Bill meta */}
            <div
              style={{
                marginBottom: "20px",
                backgroundColor: "#f9f9f9",
                padding: "16px",
                borderRadius: "8px",
                boxShadow: "0 2px 6px rgba(0,0,0,0.1)",
              }}
            >
              <p>
                <strong>Status:</strong> {randomBill.status || "N/A"}
              </p>
              <p>
                <strong>Last Action:</strong> {randomBill.last_action || "N/A"}
              </p>
            </div>

            {/* AI summary */}
            <div
              className="ai-summary"
              style={{
                backgroundColor: "#f0f4ff",
                padding: "16px",
                borderRadius: "8px",
              }}
            >
              <h4
                style={{
                  fontSize: "1.25rem",
                  marginBottom: "12px",
                  color: "#4285F4",
                }}
              >
                AI-Summarized Description
              </h4>
              <div
                dangerouslySetInnerHTML={{
                  __html: formatAiSummary(
                    randomBill.ai_summaries_enhanced?.[0]?.response_simple ||
                      "No AI summary available."
                  ),
                }}
                style={{ color: "#333", lineHeight: 1.6 }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Home;


// import React, { useState } from "react";
// import supabase from "../utils/supabase";
// import "../styles/styles.css";
// import AthenaLogo from "../assets/athena-logo.png";

// function capitalizeSentences(text) {
//   if (!text) return "";
//   return text
//     .split(/(?<=[.!?])\s+/)
//     .map((sentence) => sentence.charAt(0).toUpperCase() + sentence.slice(1).toLowerCase())
//     .join(" ");
// }

// function formatAiSummary(rawText) {
//   if (!rawText) return "No summary available.";
//   return capitalizeSentences(rawText.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>"));
// }

// const Home = () => {
//   const [randomBill, setRandomBill] = useState(null);

//   const handleRandomBill = async () => {
//     const { data, error } = await supabase
//       .from("enhanceddata")
//       .select(`*, ai_summaries_enhanced:ai_summaries_enhanced(response_simple)`)
//       .not("ai_summaries_enhanced.response_simple", "is", null);

//     if (error) {
//       console.error("Error fetching bills:", error);
//       return;
//     }

//     const filtered = data.filter((bill) => bill.ai_summaries_enhanced?.[0]?.response_simple);

//     if (filtered.length > 0) {
//       const randomIndex = Math.floor(Math.random() * filtered.length);
//       setRandomBill(filtered[randomIndex]);
//     } else {
//       console.warn("No bills found with a summary.");
//     }
//   };

//   const closeModal = () => {
//     setRandomBill(null);
//   };

//   return (
//     <div style={{
//       minHeight: "100vh",
//       background: "linear-gradient(to bottom right, #eef2f7, #ffffff)",
//       display: "flex",
//       flexDirection: "column",
//       alignItems: "center",
//       padding: "120px 20px 40px 20px",  // top more spacing for navbar
//       position: "relative",
//     }}>
      
//       {/* Big Hero Text */}
//       <h1 style={{
//         fontSize: "4rem",
//         fontWeight: "bold",
//         textAlign: "center",
//         background: "linear-gradient(270deg, #4285F4, #EA4335, #FBBC05, #34A853, #4285F4)",
//         backgroundSize: "800% 800%",
//         WebkitBackgroundClip: "text",
//         WebkitTextFillColor: "transparent",
//         animation: "rainbowTextMove 6s linear infinite",
//         marginBottom: "20px",
//       }}>
//         Democracy, Simplified
//       </h1>

//       {/* Subtext */}
//       <p style={{
//         fontSize: "1.3rem",
//         color: "#5f6368",
//         textAlign: "center",
//         maxWidth: "700px",
//         marginBottom: "40px",
//       }}>
//         Making legislation accessible and understandable for everyone with AI-powered insights and analysis.
//       </p>

//       {/* Button */}
//       <button 
//         onClick={handleRandomBill}
//         className="premium-rainbow-button"
//         style={{ marginBottom: "50px" }}
//       >
//         Show Me a Random Bill
//       </button>

//       {/* Modal Popup */}
//       {randomBill && (
//         <div className="modal-overlay">
//           <div className="modal-content" style={{ padding: "30px", maxWidth: "700px" }}>
//             <button onClick={closeModal} className="close-btn">&times;</button>

//             <h2 style={{ textAlign: "center", fontSize: "1.75rem", marginBottom: "20px" }}>
//               {randomBill.title || "Untitled Bill"}
//             </h2>

//             <div style={{
//               marginBottom: "20px",
//               backgroundColor: "#f9f9f9",
//               padding: "16px",
//               borderRadius: "8px",
//               boxShadow: "0px 2px 6px rgba(0,0,0,0.1)",
//             }}>
//               <p><strong>Status:</strong> {randomBill.status || "N/A"}</p>
//               <p><strong>Last Action:</strong> {randomBill.last_action || "N/A"}</p>
//             </div>

//             <div className="ai-summary" style={{
//               backgroundColor: "#f0f4ff",
//               padding: "16px",
//               borderRadius: "8px",
//             }}>
//               <h4 style={{ fontSize: "1.25rem", marginBottom: "12px", color: "#4285F4" }}>
//                 AI Summarized Description
//               </h4>
//               <div
//                 dangerouslySetInnerHTML={{
//                   __html: formatAiSummary(randomBill.ai_summaries_enhanced?.[0]?.response_simple || "No AI summary available."),
//                 }}
//                 style={{ color: "#333", lineHeight: "1.6" }}
//               />
//             </div>
//           </div>
//         </div>
//       )}
//     </div>
//   );
// }

// export default Home;
