import React, { useRef, useState, useEffect } from "react";
import NodeInfoPanel from "./NodeInfoPanel";
import useGraphLoader from "../hooks/useGraphLoader";
import useSigmaInstance from "../hooks/useSigmaInstance";

// Simple color input component
function ColorPicker({ color, onChange }) {
  return (
    <input
      type="color"
      value={color}
      onChange={(e) => onChange(e.target.value)}
      style={{ width: 40, height: 30, border: "none", cursor: "pointer" }}
    />
  );
}

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [fileName, setFileName] = useState("");
  const [industryColors, setIndustryColors] = useState({});
  const { graph, error } = useGraphLoader(fileContent, industryColors);

  useSigmaInstance(containerRef, graph, setSelectedNode);

  const fileInputRef = useRef(null);

  // Extract unique industries from fileContent nodes
  const industries = React.useMemo(() => {
    if (!fileContent?.nodes) return [];
    const setIndustries = new Set(fileContent.nodes.map((n) => n.industry).filter(Boolean));
    return Array.from(setIndustries);
  }, [fileContent]);

  // Initialize industry colors on new file load
  useEffect(() => {
    if (!fileContent) {
      setIndustryColors({});
      return;
    }
    // Assign random colors or keep existing ones
    setIndustryColors((oldColors) => {
      const newColors = {};
      industries.forEach((ind) => {
        newColors[ind] = oldColors[ind] || getRandomColor();
      });
      return newColors;
    });
  }, [industries, fileContent]);

  // Helper: generate random color string
  function getRandomColor() {
    // nice pastel colors
    return "#" + Math.floor(Math.random() * 0xffffff).toString(16).padStart(6, "0");
  }

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

  // Update color for a specific industry
  function updateIndustryColor(industry, color) {
    setIndustryColors((prev) => ({ ...prev, [industry]: color }));
  }

  return (
    <div style={{ display: "flex", height: "90vh" }}>
      {/* Left panel with file loader and color pickers */}
      <div
        style={{
          width: 220,
          borderRight: "1px solid #ccc",
          padding: 12,
          boxSizing: "border-box",
          overflowY: "auto",
        }}
      >
        <button
          onClick={openFileDialog}
          style={{ padding: "6px 12px", cursor: "pointer", marginBottom: 12, width: "100%" }}
        >
          Load Graph JSON
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />
        {fileName && (
          <div style={{ marginBottom: 20, fontSize: "0.9rem", color: "#555" }}>{fileName}</div>
        )}

        {industries.length > 0 && (
          <>
            <div style={{ marginBottom: 8, fontWeight: "bold" }}>Industry Colors</div>
            {industries.map((industry) => (
              <div
                key={industry}
                style={{
                  display: "flex",
                  alignItems: "center",
                  marginBottom: 8,
                  gap: 8,
                  flexWrap: "nowrap",
                }}
              >
                <div
                  style={{
                    flex: "1 1 auto",
                    whiteSpace: "nowrap",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                  }}
                  title={industry}
                >
                  {industry}
                </div>
                <ColorPicker
                  color={industryColors[industry] || "#888888"}
                  onChange={(color) => updateIndustryColor(industry, color)}
                />
              </div>
            ))}
          </>
        )}
      </div>

      {/* Main graph and info panel */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {error && (
          <div style={{ color: "red", padding: 12, backgroundColor: "#fee" }}>
            Error: {error}
          </div>
        )}

        <div style={{ flex: 1, display: "flex" }}>
          <div
            ref={containerRef}
            style={{ flex: 3, border: "1px solid #ccc", position: "relative" }}
          />
          <NodeInfoPanel node={selectedNode} />
        </div>
      </div>
    </div>
  );
}
