import React, { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import IconButton from "@mui/material/IconButton";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

export default function NodeInfoPanel({ node, onClose }) {
  const [connections, setConnections] = useState([]);
  const fileContent = useSelector((state) => state.file.content);

  // Build this once, e.g., in useEffect or memo:
  const nodeMap = React.useMemo(() => {
    const map = {};
    if (fileContent?.nodes) {
      for (let node of fileContent.nodes) {
        map[node.id] = node;
      }
    }
    return map;
  }, [fileContent]);

  // Then just do:
  const getNodeByTicker = (ticker) => nodeMap[ticker] || null;


  const getSortedUniqueTargetsBySource = (sourceTicker, edges) => {
    const seen = new Set();

    return edges
      .filter((edge) => edge.source === sourceTicker)
      .sort((a, b) => b.weight - a.weight)
      .filter((edge) => {
        if (seen.has(edge.target)) return false;
        seen.add(edge.target);
        return true;
      })
      .map((edge) => edge.target);
  };

  useEffect(() => {
    if (node && fileContent && fileContent.edges) {
      setConnections(getSortedUniqueTargetsBySource(node.label, fileContent.edges));
    } else {
      setConnections([]);
    }
  }, [node, fileContent]);

  return (
    <div
      style={{
        flex: "0 0 280px", // fixed width
        height: "100vh",   // full viewport height
        padding: "10px",
        borderLeft: "1px solid #ccc",
        background: "#CECECC",
        position: "relative",
        overflowY: "auto", // scroll only inside this panel
        boxSizing: "border-box",
      }}
    >
      {/* Close Button */}
      <IconButton
        onClick={onClose}
        size="small"
        sx={{
          position: "absolute",
          top: 8,
          right: 8,
          color: "#333",
          zIndex: 1,
        }}
        title="Close panel"
      >
        <FontAwesomeIcon icon={faTimes} />
      </IconButton>

      <h3 style={{ marginTop: 0 }}>Information Pane</h3>

      {node ? (
        <div>
          <p><strong>{node.label}</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Industry:</strong> {node.industry}
          </p>
          <p style={{ fontSize: "0.85em" }}>
            <strong>Centrality Measures:</strong>
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Closeness Centrality:</strong> {node.closeness_centrality?.toFixed(4)}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Harmonic Closeness Centrality:</strong>{" "}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Betweenness Centrality:</strong> {node.betweenness_centrality?.toFixed(4)}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Eigenvector Centrality:</strong> {node.eigenvector_centrality?.toFixed(4)}
          </p>
          <p style={{ fontSize: "0.85em" }}>
            <strong>Other Measures:</strong>
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Degree:</strong>{" "}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Weighted Degree:</strong>{" "}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Eccentricity:</strong>{" "}
          </p>
          <p><strong>Connections:</strong></p>
          <p style={{ marginLeft: "5px", fontSize: "0.85em" }}>
            <strong>Connected Firms ({connections.length})</strong>
          </p>
          <ul style={{ marginLeft: "20px", fontSize: "0.85em" }}>
            {connections.map((ticker) => (
              <li key={ticker}>{ticker} ({getNodeByTicker(ticker).industry})</li>
            ))}
          </ul>
        </div>
      ) : (
        <p>Click a node to view details</p>
      )}
    </div>
  );
}
