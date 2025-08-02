import React, { useEffect, useState } from "react";
import Tooltip from "@mui/material/Tooltip"; // Import Tooltip
import { useSelector, useDispatch } from "react-redux";  // added useDispatch
import IconButton from "@mui/material/IconButton";
import Button from "@mui/material/Button";  // added Button
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes, faTrash, faPlus } from "@fortawesome/free-solid-svg-icons";
import { removeNode } from "../store/fileSlice";  // import your removeNode action

export default function NodeInfoPanel({ node, onClose, simulateClick }) {
  const dispatch = useDispatch();
  const [connections, setConnections] = useState([]);
  const fileContent = useSelector((state) => state.file.content);
  const industryColors = useSelector((state) => state.file.industryColors);

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

  const getSortedUniqueConnections = (ticker, edges) => {
    const seen = new Set();
    const connections = [];

    edges
      .filter(edge => edge.source === ticker || edge.target === ticker)
      .sort((a, b) => b.weight - a.weight)
      .forEach(edge => {
        const other = edge.source === ticker ? edge.target : edge.source;
        if (!seen.has(other)) {
          seen.add(other);
          connections.push(other);
        }
      });

    return connections;
  };

  useEffect(() => {
    if (node && fileContent?.edges) {
      setConnections(getSortedUniqueConnections(node.label, fileContent.edges));
    } else {
      setConnections([]);
    }
  }, [node, fileContent]);

  const formatDecimals = (value) => {
    if (typeof value !== "number") return "";

    if (Number.isInteger(value)) {
      return value.toFixed(1);
    }

    const rounded = Number(value.toFixed(4));
    const decimals = rounded.toString().split(".")[1] || "";

    if (decimals.length >= 3 && decimals[2] !== "0") {
      return rounded.toFixed(3);
    } else if (decimals.length >= 2 && decimals[1] !== "0") {
      return rounded.toFixed(2);
    } else {
      return rounded.toFixed(1);
    }
  };

  const handleRemoveNode = () => {
    if (!node || !fileContent?.nodes) return;

    // Remove the current node
    dispatch(removeNode(node.id));

    // Get the remaining nodes after removal
    const remainingNodes = fileContent.nodes.filter(n => n.id !== node.id);

    if (remainingNodes.length === 0) return; // No nodes left

    // Find the node with the highest eigenvector centrality
    const mostCentral = remainingNodes.reduce((maxNode, currentNode) => {
      return (currentNode.eigenvector_centrality || 0) > (maxNode.eigenvector_centrality || 0)
        ? currentNode
        : maxNode;
    }, remainingNodes[0]);

    // Simulate click to update the panel with the most central node
    simulateClick(mostCentral.id);
  };

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

      <h3 style={{ marginTop: 0,  marginBottom: 0 }}>Information Pane</h3>
      <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
        {/* Add Node */}
        <Tooltip title="Add node" arrow placement="top">
          <IconButton
            // onClick={handleAddNode}
            size="small"
            sx={{
              backgroundColor: "transparent",
              color: "#1976d2",
              "&:hover": {
                backgroundColor: "#fff",
              },
            }}
          >
            <FontAwesomeIcon icon={faPlus} />
          </IconButton>
        </Tooltip>

        {/* Remove Node */}
        <Tooltip title="Remove node" arrow placement="top">
          <IconButton
            onClick={handleRemoveNode}
            size="small"
            sx={{
              backgroundColor: "transparent",
              color: "#1976d2",
              "&:hover": {
                backgroundColor: "#fff",
              },
            }}
          >
            <FontAwesomeIcon icon={faTrash} />
          </IconButton>
        </Tooltip>
      </div>


      {node ? (
        <div>
          <p><strong>{node.label}</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Industry:</strong> {node.industry}
          </p>

          <p style={{ fontSize: "0.85em" }}><strong>Centrality Measures:</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Closeness Centrality:</strong> {formatDecimals(node.closeness_centrality)}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Harmonic Closeness Centrality:</strong>{formatDecimals(node.harmonic_centrality)}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Betweenness Centrality:</strong> {formatDecimals(node.betweenness_centrality)}
          </p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}>
            <strong>Eigenvector Centrality:</strong> {formatDecimals(node.eigenvector_centrality)}
          </p>

          <p style={{ fontSize: "0.85em" }}><strong>Other Measures:</strong></p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}><strong>Degree:</strong>{formatDecimals(node.degree)}</p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}><strong>Weighted Degree:</strong>{formatDecimals(node.weighted_degree)}</p>
          <p style={{ marginLeft: "16px", fontSize: "0.85em" }}><strong>Eccentricity:</strong>{formatDecimals(node.eccentricity)}</p>

          <p><strong>Connections:</strong></p>
          <p style={{ marginLeft: "5px", fontSize: "0.85em" }}>
            <strong>Connected Firms ({connections.length})</strong>
          </p>
          <ul style={{ marginLeft: "5px", fontSize: "0.85em", listStyleType: "none", padding: 0 }}>
            {connections.map((ticker) => {
              const connNode = getNodeByTicker(ticker);
              if (!connNode) return null;

              const color = industryColors[connNode.industry] || "#000";

              return (
                <li key={ticker} style={{ display: "flex", alignItems: "center", marginBottom: 4 }}>
                  {/* Color square */}
                  <span
                    style={{
                      display: "inline-block",
                      width: 12,
                      height: 12,
                      backgroundColor: color,
                      marginRight: 8,
                      borderRadius: 2,
                      flexShrink: 0,
                    }}
                    title={`Industry color: ${connNode.industry}`}
                  />
                  
                  {/* Ticker + industry */}
                  <span
                    onClick={() => simulateClick(connNode.id)}
                    style={{ color: "#0055cc", textDecoration: "underline", cursor: "pointer" }}
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
