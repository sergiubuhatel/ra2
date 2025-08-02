import React, { useEffect, useState, useMemo } from "react";
import { useSelector, useDispatch } from "react-redux";
import {
  IconButton,
  Tooltip,
} from "@mui/material";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes, faTrash, faPlus } from "@fortawesome/free-solid-svg-icons";
import { removeNode, addNodeWithEdges } from "../store/fileSlice";
import AddNodeDialog from "./AddNodeDialog";

export default function NodeInfoPanel({ node, onClose, simulateClick }) {
  const dispatch = useDispatch();
  const fileContent = useSelector((state) => state.file.content);
  const industryColors = useSelector((state) => state.file.industryColors);
  const [connections, setConnections] = useState([]);
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [newNodeTicker, setNewNodeTicker] = useState("");
  const [selectedConnections, setSelectedConnections] = useState({});

  const nodeMap = useMemo(() => {
    const map = {};
    fileContent?.nodes?.forEach((node) => (map[node.id] = node));
    return map;
  }, [fileContent]);

  const getNodeByTicker = (ticker) => nodeMap[ticker] || null;

  const getSortedUniqueConnections = (ticker, edges) => {
    const seen = new Set();
    const connections = [];

    edges
      .filter((edge) => edge.source === ticker || edge.target === ticker)
      .sort((a, b) => b.weight - a.weight)
      .forEach((edge) => {
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

  const handleRemoveNode = () => {
    if (!node) return;

    dispatch(removeNode(node.id));
    const remainingNodes = fileContent.nodes?.filter((n) => n.id !== node.id) || [];

    if (remainingNodes.length > 0) {
      const mostCentral = remainingNodes.reduce((a, b) =>
        (a.eigenvector_centrality || 0) > (b.eigenvector_centrality || 0) ? a : b
      );
      simulateClick(mostCentral.id);
    }
  };

  const openAddDialog = () => {
    setNewNodeTicker("");
    setSelectedConnections({});
    setAddDialogOpen(true);
  };

  const closeAddDialog = () => setAddDialogOpen(false);

  const toggleConnection = (nodeId) => {
    setSelectedConnections((prev) => {
      const updated = { ...prev };
      if (updated[nodeId]) delete updated[nodeId];
      else updated[nodeId] = 1;
      return updated;
    });
  };

  const handleWeightChange = (nodeId, weight) => {
    setSelectedConnections((prev) => ({
      ...prev,
      [nodeId]: weight,
    }));
  };

  const handleAddNodeSubmit = () => {
    if (!newNodeTicker.trim()) return alert("Please enter a ticker.");

    const newNodeId = `node-${Date.now()}`;
    const edges = Object.entries(selectedConnections).map(([targetId, weight]) => ({
      source: newNodeId,
      target: targetId,
      weight: parseFloat(weight),
    }));

    const node = {
      id: newNodeId,
      label: newNodeTicker.trim(),
      industry: "Unknown",
    };

    dispatch(addNodeWithEdges({ node, edges }));
    setAddDialogOpen(false);
    simulateClick(newNodeId);
  };

  const formatDecimals = (val) => {
    if (typeof val !== "number") return "";
    const rounded = Number(val.toFixed(4));
    return rounded % 1 === 0 ? rounded.toFixed(1) : rounded.toString();
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
        sx={{ position: "absolute", top: 8, right: 8, color: "#333" }}
        title="Close panel"
      >
        <FontAwesomeIcon icon={faTimes} />
      </IconButton>

      <h3 style={{ marginTop: 0 }}>Information Pane</h3>

      <div style={{ display: "flex", gap: "8px", marginTop: "8px" }}>
        <Tooltip title="Add node" arrow placement="top">
          <IconButton onClick={openAddDialog} size="small" sx={{ color: "#1976d2" }}>
            <FontAwesomeIcon icon={faPlus} />
          </IconButton>
        </Tooltip>

        <Tooltip title="Remove node" arrow placement="top">
          <IconButton onClick={handleRemoveNode} size="small" sx={{ color: "#1976d2" }}>
            <FontAwesomeIcon icon={faTrash} />
          </IconButton>
        </Tooltip>
      </div>

      <AddNodeDialog
        open={addDialogOpen}
        onClose={closeAddDialog}
        onSubmit={handleAddNodeSubmit}
        newNodeTicker={newNodeTicker}
        setNewNodeTicker={setNewNodeTicker}
        selectedConnections={selectedConnections}
        toggleConnection={toggleConnection}
        handleWeightChange={handleWeightChange}
        existingNodes={fileContent?.nodes?.filter((n) => n.id !== node?.id) || []}
      />

      {node ? (
        <div>
          <p><strong>{node.label}</strong></p>
          <p style={{ marginLeft: 16, fontSize: "0.85em" }}>
            <strong>Industry:</strong> {node.industry}
          </p>

          <p style={{ fontSize: "0.85em" }}><strong>Centrality Measures:</strong></p>
          <p style={{ marginLeft: 16, fontSize: "0.85em" }}>
            Closeness: {formatDecimals(node.closeness_centrality)}
          </p>
          <p style={{ marginLeft: 16, fontSize: "0.85em" }}>
            Harmonic: {formatDecimals(node.harmonic_centrality)}
          </p>
          <p style={{ marginLeft: 16, fontSize: "0.85em" }}>
            Betweenness: {formatDecimals(node.betweenness_centrality)}
          </p>
          <p style={{ marginLeft: 16, fontSize: "0.85em" }}>
            Eigenvector: {formatDecimals(node.eigenvector_centrality)}
          </p>

          <p style={{ fontSize: "0.85em" }}><strong>Other:</strong></p>
          <p style={{ marginLeft: 16, fontSize: "0.85em" }}>
            Degree: {formatDecimals(node.degree)} | Weighted: {formatDecimals(node.weighted_degree)}
          </p>
          <p style={{ marginLeft: 16, fontSize: "0.85em" }}>
            Eccentricity: {formatDecimals(node.eccentricity)}
          </p>

          <p><strong>Connections</strong></p>
          <ul style={{ fontSize: "0.85em", marginLeft: 10, listStyle: "none", padding: 0 }}>
            {connections.map((ticker) => {
              const connNode = getNodeByTicker(ticker);
              if (!connNode) return null;
              const color = industryColors[connNode.industry] || "#000";
              return (
                <li key={ticker} style={{ marginBottom: 4 }}>
                  <span
                    style={{
                      display: "inline-block",
                      width: 12,
                      height: 12,
                      backgroundColor: color,
                      marginRight: 8,
                      borderRadius: 2,
                      verticalAlign: "middle",
                    }}
                  />
                  <span
                    onClick={() => simulateClick(connNode.id)}
                    style={{ color: "#0055cc", textDecoration: "underline", cursor: "pointer" }}
                  >
                    {connNode.label} ({connNode.industry})
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
