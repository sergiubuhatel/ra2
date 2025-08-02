// src/components/NodeStats.js
import React from "react";

export default function NodeStats({ node, industryColors, onConnectionClick }) {
  const formatDecimals = (val) => {
    if (typeof val !== "number") return "";
    const rounded = Number(val.toFixed(4));
    return rounded % 1 === 0 ? rounded.toFixed(1) : rounded.toString();
  };

  return (
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

      {node.connections?.length > 0 && (
        <>
          <p><strong>Connections</strong></p>
          <ul style={{ fontSize: "0.85em", marginLeft: 10, listStyle: "none", padding: 0 }}>
            {node.connections.map((connNode) => {
              const color = industryColors[connNode.industry] || "#000";
              return (
                <li key={connNode.id} style={{ marginBottom: 4 }}>
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
                    onClick={() => onConnectionClick(connNode.id)}
                    style={{ color: "#0055cc", textDecoration: "underline", cursor: "pointer" }}
                  >
                    {connNode.label} ({connNode.industry})
                  </span>
                </li>
              );
            })}
          </ul>
        </>
      )}
    </div>
  );
}
