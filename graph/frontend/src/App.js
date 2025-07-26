import React from "react";
import { useSelector } from "react-redux";
import NetworkGraph from "./components/NetworkGraph";

function App() {
  const selectedYear = useSelector((state) => state.file.selectedYear);
  const selectedFilter = useSelector((state) => state.file.selectedFilter);

  return (
    <div style={{ background: "black", minHeight: "100vh", padding: "10px" }}>
      <h1
        style={{
          textAlign: "center",
          color: "white",
          fontSize: "2rem",
          fontWeight: "bold",
          marginBottom: "40px",
        }}
      >
        {selectedFilter} Industries in {selectedYear}
      </h1>
      <NetworkGraph />
    </div>
  );
}

export default App;
