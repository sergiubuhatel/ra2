import React from "react";
import NetworkGraph from "./components/NetworkGraph";

function App() {
  return (
    <div style={{ background: "black", minHeight: "100vh", padding: "10px" }}>
      <h1 style={{ 
        textAlign: "center", 
        color: "white", 
        fontSize: "3rem", 
        fontWeight: "bold", 
        marginBottom: "40px" 
      }}>
        Stock Network
      </h1>
      <NetworkGraph />
    </div>
  );
}

export default App;
