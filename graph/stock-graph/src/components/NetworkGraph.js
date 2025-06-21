import React, { useRef, useState } from "react";
import NodeInfoPanel from "./NodeInfoPanel";
import useGraphLoader from "./hooks/useGraphLoader";
import useSigmaInstance from "./hooks/useSigmaInstance";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [fileName, setFileName] = useState("");
  const { graph, error } = useGraphLoader(fileContent);
  useSigmaInstance(containerRef, graph, setSelectedNode);

  const fileInputRef = useRef(null);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        setFileContent(json);
      } catch {
        alert("Invalid JSON file");
        setFileContent(null);
      }
    };
    reader.readAsText(file);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  return (
    <div style={{ display: "flex", height: "90vh", flexDirection: "column" }}>
      <div
        style={{
          marginBottom: 10,
          display: "flex",
          flexDirection: "column",
          alignItems: "flex-start",
          width: "max-content",
        }}
      >
        <button
          onClick={openFileDialog}
          style={{ padding: "6px 12px", cursor: "pointer", marginLeft: 12 }}
        >
          Graph File
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        {fileName && (
          <div
            style={{
              marginTop: 8,
              fontSize: "0.9rem",
              color: "#555",
              marginLeft: 12,
            }}
          >
            {fileName}
          </div>
        )}
      </div>

      {error && <div style={{ color: "red" }}>Error: {error}</div>}

      <div style={{ display: "flex", flex: 1 }}>
        <div
          ref={containerRef}
          style={{ flex: 3, border: "1px solid #ccc", position: "relative" }}
        >
          {/* Circle overlay removed */}
        </div>
        <NodeInfoPanel node={selectedNode} />
      </div>
    </div>
  );
}
