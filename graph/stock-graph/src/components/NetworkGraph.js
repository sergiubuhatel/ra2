import React, { useRef, useState } from "react";
import NodeInfoPanel from "./NodeInfoPanel";
import useGraphLoader from "./hooks/useGraphLoader";
import useSigmaInstance from "./hooks/useSigmaInstance";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [fileContent, setFileContent] = useState(null);

  // Pass the loaded file content JSON to useGraphLoader
  const { graph, error } = useGraphLoader(fileContent);
  useSigmaInstance(containerRef, graph, setSelectedNode);

  // Handle file selection
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();

    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        setFileContent(json); // Pass JSON to loader hook
      } catch (err) {
        alert("Invalid JSON file");
        setFileContent(null);
      }
    };

    reader.readAsText(file);
  };

  return (
    <div style={{ display: "flex", height: "90vh", flexDirection: "column" }}>
      <div style={{ marginBottom: 10 }}>
        <input type="file" accept=".json" onChange={handleFileChange} />
      </div>

      {error && <div style={{ color: "red" }}>Error: {error}</div>}

      <div style={{ display: "flex", flex: 1 }}>
        <div
          ref={containerRef}
          style={{ flex: 3, border: "1px solid #ccc", position: "relative" }}
        />
        <NodeInfoPanel node={selectedNode} />
      </div>
    </div>
  );
}
