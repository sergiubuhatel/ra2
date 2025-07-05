import React from "react";
import IconButton from "@mui/material/IconButton";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faTimes } from "@fortawesome/free-solid-svg-icons";

export default function NodeInfoPanel({ node, onClose }) {
  return (
    <div
      style={{
        flex: "0 0 280px",  // fixed width
        padding: "10px",
        borderLeft: "1px solid #ccc",
        background: "#CECECC",
        position: "relative",
        overflowY: "auto",
        boxSizing: "border-box",
      }}
    >
      {/* X Button using MUI + Font Awesome */}
      <IconButton
        onClick={onClose}
        size="small"
        sx={{
          position: "absolute",
          top: 8,
          right: 8,
          color: "#333",
        }}
        title="Close panel"
      >
        <FontAwesomeIcon icon={faTimes} />
      </IconButton>

      <h3 style={{ marginTop: 0 }}>Node Info</h3>

      {node ? (
        <div>
          <p>
            <strong>Ticker:</strong> {node.label}
          </p>
          <p>
            <strong>Industry:</strong> {node.industry}
          </p>
          <p>
            <strong>Eigenvector Centrality:</strong>{" "}
            {node.eigenvector_centrality?.toFixed(4)}
          </p>
          <p>
            <strong>Betweenness Centrality:</strong>{" "}
            {node.betweenness_centrality?.toFixed(4)}
          </p>
          <p>
            <strong>Closeness Centrality:</strong>{" "}
            {node.closeness_centrality?.toFixed(4)}
          </p>
          <p>
            <strong>Degree Centrality:</strong>{" "}
            {node.degree_centrality?.toFixed(4)}
          </p>
        </div>
      ) : (
        <p>Click a node to view details</p>
      )}
    </div>
  );
}
