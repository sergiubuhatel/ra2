import React from "react";
import NetworkGraph from "./components/NetworkGraph";

function App() {
  return (
    <div style={{ background: "black", minHeight: "100vh", padding: "10px" }}>
      <h1 style={{ 
        textAlign: "center", 
        color: "white", 
        fontSize: "2rem", 
        fontWeight: "bold", 
        marginBottom: "40px" 
      }}>
        Top 50 Industries in 2017
      </h1>
      <NetworkGraph />
    </div>
  );
}

export default App;
