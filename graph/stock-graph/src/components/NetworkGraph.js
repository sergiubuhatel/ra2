import React, { useEffect, useRef, useState } from "react";
import Graph from "graphology";
import { circular } from "graphology-layout";
import { Sigma } from "sigma";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const sigmaInstanceRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/graph_top50.json")
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

        // Add nodes
        data.nodes.forEach((node) => {
          graph.addNode(node.id, {
            label: node.label,
            industry: node.industry,
            size: 5,
            color: "#0074D9",
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
              color: "#CCC",
            });
          }
        });

        // Apply layout
        circular.assign(graph);

        // Initialize Sigma
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
