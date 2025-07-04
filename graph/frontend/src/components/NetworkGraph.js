import React, { useRef, useState, useEffect } from "react";
import NodeInfoPanel from "./NodeInfoPanel";
import useGraphLoader from "../hooks/useGraphLoader";
import useSigmaInstance from "../hooks/useSigmaInstance";
import { getDeterministicColor } from "../utils/colors";
import GraphControlsPanel from "./GraphControlsPanel";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [fileName, setFileName] = useState("");
  const [industryColors, setIndustryColors] = useState({});
  const [nodeSizeFactor, setNodeSizeFactor] = useState(25);
  const [edgeThickness, setEdgeThickness] = useState(1);

  const { graph, error } = useGraphLoader(
    fileContent,
    industryColors,
    edgeThickness,
    nodeSizeFactor
  );

  useSigmaInstance(containerRef, graph, setSelectedNode);

  const fileInputRef = useRef(null);

  const industries = React.useMemo(() => {
    if (!fileContent?.nodes) return [];
    const setIndustries = new Set(
      fileContent.nodes.map((n) => n.industry).filter(Boolean)
    );
    return Array.from(setIndustries);
  }, [fileContent]);

  useEffect(() => {
    if (!fileContent) {
      setIndustryColors({});
      return;
    }

    setIndustryColors((oldColors) => {
      const newColors = {};
      industries.forEach((ind) => {
        newColors[ind] = oldColors[ind] || getDeterministicColor(ind);
      });
      return newColors;
    });
  }, [industries, fileContent]);

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

  function updateIndustryColor(industry, color) {
    setIndustryColors((prev) => ({ ...prev, [industry]: color }));
  }

  return (
    <div style={{ display: "flex", height: "90vh" }}>
      <GraphControlsPanel
        fileInputRef={fileInputRef}
        openFileDialog={openFileDialog}
        handleFileChange={handleFileChange}
        fileName={fileName}
        industries={industries}
        industryColors={industryColors}
        updateIndustryColor={updateIndustryColor}
        nodeSizeFactor={nodeSizeFactor}
        setNodeSizeFactor={setNodeSizeFactor}
        edgeThickness={edgeThickness}
        setEdgeThickness={setEdgeThickness}
      />

      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {error && (
          <div style={{ color: "red", padding: 12, backgroundColor: "#fee" }}>
            Error: {error}
          </div>
        )}
        <div style={{ flex: 1, display: "flex" }}>
          <div
            ref={containerRef}
            style={{
              flex: 3,
              border: "1px solid #ccc",
              position: "relative",
              background: "#000200",
            }}
          />
          {selectedNode && (
            <NodeInfoPanel node={selectedNode} onClose={() => setSelectedNode(null)} />
          )}
        </div>
      </div>
    </div>
  );
}
