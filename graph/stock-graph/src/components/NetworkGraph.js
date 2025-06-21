import React, { useRef, useState } from "react";
import NodeInfoPanel from "./NodeInfoPanel";
import useGraphLoader from "./hooks/useGraphLoader";
import useSigmaInstance from "./hooks/useSigmaInstance";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [fileName, setFileName] = useState(""); // Track the filename

  const { graph, error } = useGraphLoader(fileContent);
  useSigmaInstance(containerRef, graph, setSelectedNode);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setFileName(file.name); // Save filename to state

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        setFileContent(json);
      } catch (err) {
        alert("Invalid JSON file");
        setFileContent(null);
      }
    };
    reader.readAsText(file);
  };

  return (
    <div style={{ display: "flex", height: "90vh", flexDirection: "column" }}>
      {/* File input and filename stacked vertically */}
      <div
        style={{
          marginBottom: 10,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          width: "max-content",
        }}
      >
        <input
          type="file"
          accept=".json"
          onChange={handleFileChange}
          style={{ display: "block" }}
        />
        {fileName && (
          <div style={{ marginTop: 8, fontSize: "0.9rem", color: "#555" }}>
            Loaded file: {fileName}
          </div>
        )}
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
