// NodeInfoPanel.js
import React from "react";

export default function NodeInfoPanel({ node }) {
  return (
    <div
      style={{
        flex: 1,
        padding: "10px",
        borderLeft: "1px solid #ccc",
        background: "#f9f9f9",
        overflowY: "auto",
      }}
    >
      <h3>Node Info</h3>
      {node ? (
        <div>
          <p><strong>Ticker:</strong> {node.label}</p>
          <p><strong>Industry:</strong> {node.industry}</p>
          <p><strong>Eigenvector Centrality:</strong> {node.eigenvector_centrality?.toFixed(4)}</p>
          <p><strong>Betweenness Centrality:</strong> {node.betweenness_centrality?.toFixed(4)}</p>
          <p><strong>Closeness Centrality:</strong> {node.closeness_centrality?.toFixed(4)}</p>
          <p><strong>Degree Centrality:</strong> {node.degree_centrality?.toFixed(4)}</p>
        </div>
      ) : (
        <p>Click a node to view details</p>
      )}
    </div>
  );
}
