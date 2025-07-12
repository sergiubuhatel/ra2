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

      <h3 style={{ marginTop: 0 }}>Information Pane</h3>

      {node ? (
        <div>
          <p>
            <strong>{node.label}</strong> 
          </p>
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
              <strong>Industry:</strong> {node.industry}
          </p>
          <p style={{ fontSize: '0.85em' }}>
            <strong>Centrality Measures:</strong> 
          </p>
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
            <strong>Closeness Centrality:</strong>{" "}
            {node.closeness_centrality?.toFixed(4)}
          </p>          
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
            <strong>Harmonic Closeness Centrality:</strong>{" "}
          </p>          
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
            <strong>Betweenness Centrality:</strong>{" "}
            {node.betweenness_centrality?.toFixed(4)}
          </p>
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
            <strong>Eigenvector Centrality:</strong>{" "}
            {node.eigenvector_centrality?.toFixed(4)}
          </p>
          <p style={{ fontSize: '0.85em' }}>
            <strong>Other Measures:</strong> 
          </p>
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
            <strong>Degree:</strong>{" "}
          </p>          
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
            <strong>Weighted Degree:</strong>{" "}
          </p>          
          <p style={{ marginLeft: '16px', fontSize: '0.85em' }}>
            <strong>Eccentricity:</strong>{" "}
          </p>          
          <p>
            <strong>Connections:</strong> 
          </p>
          <p style={{ marginLeft: '5px', fontSize: '0.85em' }}>
            <strong>Connected Firms ()</strong> 
          </p>
        </div>
      ) : (
        <p>Click a node to view details</p>
      )}
    </div>
  );
}
