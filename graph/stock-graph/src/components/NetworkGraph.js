import React, { useEffect, useRef, useState } from "react";
import Graph from "graphology";
import { circular } from "graphology-layout";
import { Sigma } from "sigma";
import chroma from "chroma-js"; // Optional: for color scaling

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const sigmaInstanceRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/graph_with_centrality.json") // Make sure it's in public/
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load graph data");
        return res.json();
      })
      .then((data) => {
        if (!data.nodes || !Array.isArray(data.nodes)) {
          throw new Error("Invalid graph: 'nodes' array missing");
        }
        if (!data.edges || !Array.isArray(data.edges)) {
          throw new Error("Invalid graph: 'edges' array missing");
        }

        const graph = new Graph();

        // Get max centrality for scaling
        const maxCentrality = Math.max(
          ...data.nodes.map((n) => n.eigenvector_centrality || 0)
        );

        // Add nodes
        data.nodes.forEach((node) => {
          const centrality = node.eigenvector_centrality || 0;
          const scaledSize = 5 + 20 * (centrality / maxCentrality);
          const scaledColor = chroma
            .scale(["#b0d0ff", "#003399"])
            .mode("lab")(centrality / maxCentrality)
            .hex();

          graph.addNode(node.id, {
            label: node.label,
            industry: node.industry,
            size: scaledSize,
            color: scaledColor,
            ...node, // optional: attach all centrality values for debugging/tooltip
          });
        });

        // Add edges
        data.edges.forEach((edge, i) => {
          const edgeId = `e${i}`;
          if (
            graph.hasNode(edge.source) &&
            graph.hasNode(edge.target) &&
            !graph.hasEdge(edge.source, edge.target)
          ) {
            graph.addEdgeWithKey(edgeId, edge.source, edge.target, {
              size: Math.log(edge.weight || 1),
              color: "#ccc",
            });
          }
        });

        // Layout
        circular.assign(graph);

        // Init Sigma
        if (sigmaInstanceRef.current) sigmaInstanceRef.current.kill();
        sigmaInstanceRef.current = new Sigma(graph, containerRef.current);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
      });

    return () => {
      if (sigmaInstanceRef.current) {
        sigmaInstanceRef.current.kill();
        sigmaInstanceRef.current = null;
      }
    };
  }, []);

  if (error) return <div style={{ color: "red" }}>Error: {error}</div>;

  return (
    <div
      ref={containerRef}
      style={{ height: "90vh", width: "100%", border: "1px solid #ccc" }}
    />
  );
}
