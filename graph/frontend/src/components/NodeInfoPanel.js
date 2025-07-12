import React, { useEffect, useState, useMemo } from "react";
import { useSelector } from "react-redux";
import IconButton from "@mui/material/IconButton";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

export default function NodeInfoPanel({ node, onClose, onSelectNode }) {
  const [connections, setConnections] = useState([]);
  const fileContent = useSelector((state) => state.file.content);

  const nodeMap = React.useMemo(() => {
    const map = {};
    if (fileContent?.nodes) {
      for (let node of fileContent.nodes) {
        map[node.id] = node;
      }
    }
    return map;
  }, [fileContent]);

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
    if (node && fileContent?.edges) {
      setConnections(getSortedUniqueTargetsBySource(node.label, fileContent.edges));
    } else {
      setConnections([]);
    }
  }, [node, fileContent]);

  return (
    <div
      style={{
        flex: "0 0 280px",
        height: "100vh",
        padding: "10px",
        borderLeft: "1px solid #ccc",
        background: "#CECECC",
        position: "relative",
        overflowY: "auto",
        boxSizing: "border-box",
      }}
    >
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

          {/* Centralities */}
          <p style={{ fontSize: "0.85em" }}><strong>Centrality Measures:</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Closeness Centrality:</strong> {node.closeness_centrality?.toFixed(4)}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Harmonic Closeness Centrality:</strong>
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Betweenness Centrality:</strong> {node.betweenness_centrality?.toFixed(4)}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Eigenvector Centrality:</strong> {node.eigenvector_centrality?.toFixed(4)}
          </p>

          {/* Other Measures */}
          <p style={{ fontSize: "0.85em" }}><strong>Other Measures:</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}><strong>Degree:</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}><strong>Weighted Degree:</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}><strong>Eccentricity:</strong></p>

          {/* Connections */}
          <p><strong>Connections:</strong></p>
          <p style={{ marginLeft: "5px", fontSize: "0.85em" }}>
            <strong>Connected Firms ({connections.length})</strong>
          </p>
          <ul style={{ marginLeft: "20px", fontSize: "0.85em", listStyleType: "none", padding: 0 }}>
            {connections.map((ticker) => {
              const connNode = getNodeByTicker(ticker);
              if (!connNode) return null;
              return (
                <li key={ticker} style={{ cursor: "pointer", marginBottom: 4 }}>
                  <span
                    onClick={() => onSelectNode(connNode)}
                    style={{ color: "#0055cc", textDecoration: "underline" }}
                    title="Click to view node"
                  >
                    {ticker} ({connNode.industry})
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      ) : (
        <p>Click a node to view details</p>
      )}
    </div>
  );
}
