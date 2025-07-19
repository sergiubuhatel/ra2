import React, { useRef, useState, useEffect, useMemo } from "react";
import { useDispatch, useSelector } from "react-redux";
import NodeInfoPanel from "./NodeInfoPanel";
import useGraphLoader from "../hooks/useGraphLoader";
import useSigmaInstance from "../hooks/useSigmaInstance";
import { getDeterministicColor } from "../utils/colors";
import GraphControlsPanel from "./GraphControlsPanel";
import {
  setFileContent,
  setFileName,
  setIndustries,
  setIndustryColors,
  updateIndustryColor as updateIndustryColorAction,
} from "../store/fileSlice";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const fileInputRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [nodeSizeFactor, setNodeSizeFactor] = useState(25);
  const [edgeThickness, setEdgeThickness] = useState(1);

  const dispatch = useDispatch();

  const fileContent = useSelector((state) => state.file.content);
  const fileName = useSelector((state) => state.file.name);
  const industries = useSelector((state) => state.file.industries);
  const industryColors = useSelector((state) => state.file.industryColors);

  // Load graph
  const { graph, error } = useGraphLoader(
    fileContent,
    industryColors,
    edgeThickness,
    nodeSizeFactor
  );

  const simulateClick = useSigmaInstance(containerRef, graph, setSelectedNode);

  const calculatedIndustries = useMemo(() => {
    if (!fileContent?.nodes) return [];
    const setIndustries = new Set(
      fileContent.nodes.map((n) => n.industry).filter(Boolean)
    );
    return Array.from(setIndustries);
  }, [fileContent]);

  const rgbToHex = (r, g, b) =>
  '#' + [r, g, b].map(x => x.toString(16).padStart(2, '0')).join('');

  // Set industries and their colors in Redux on file load
  useEffect(() => {
    if (!fileContent) {
      dispatch(setIndustries([]));
      dispatch(setIndustryColors({}));
      return;
    }

    dispatch(setIndustries(calculatedIndustries));

    const defaultColors = {};
    calculatedIndustries.forEach((ind) => {
      defaultColors[ind] =
        industryColors[ind] || getDeterministicColor(ind);
    });
    defaultColors["Comps"] = rgbToHex(242, 205, 249);
    defaultColors["BusSv"] = rgbToHex(17, 229, 232);
    defaultColors["Fun"] = rgbToHex(203, 216, 24);
    defaultColors["Unclassified"] = rgbToHex(42, 213, 71);
    defaultColors["Chips"] = rgbToHex(206, 155, 13);

    dispatch(setIndustryColors(defaultColors));

  }, [fileContent, calculatedIndustries]);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) {
      dispatch(setFileContent(null));
      return;
    }

    dispatch(setFileName(file.name));

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target.result);
        dispatch(setFileContent(json));
      } catch {
        alert("Invalid JSON file");
        dispatch(setFileContent(null));
      }
    };
    reader.readAsText(file);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const updateIndustryColor = (industry, color) => {
    dispatch(updateIndustryColorAction({ industry, color }));
  };

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
            <NodeInfoPanel
              node={selectedNode}
              onClose={() => setSelectedNode(null)}
              simulateClick={simulateClick}
            />
          )}
        </div>
      </div>
    </div>
  );
}
