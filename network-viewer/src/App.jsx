import React from "react";
import GraphViewer from "./components/GraphViewer.jsx";  // force .jsx

function App() {
  return (
    <div style={{ padding: "20px" }}>
      <h2>Company Network Viewer</h2>
      <GraphViewer />
    </div>
  );
}

export default App;
