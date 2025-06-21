import React, { useEffect, useRef, useState } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { Sigma } from "sigma";
import chroma from "chroma-js";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const sigmaInstanceRef = useRef(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/graph_with_centrality.json")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load graph data");
        return res.json();
      })
      .then((data) => {
        if (!data.nodes || !Array.isArray(data.nodes))
          throw new Error("Invalid graph: 'nodes' array missing");
        if (!data.edges || !Array.isArray(data.edges))
          throw new Error("Invalid graph: 'edges' array missing");

        const graph = new Graph();

        const maxCentrality = Math.max(
          ...data.nodes.map((n) => n.eigenvector_centrality || 0)
        );

        // Add nodes with size scaled by centrality
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
            // initial coords will be set by layout
            x: Math.random(),
            y: Math.random(),
            mass: scaledSize, // mass to attract bigger nodes more
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
              size: Math.log((edge.weight || 1) + 1),
              color: "#999",
            });
          }
        });

        // Run ForceAtlas2 layout with settings to cluster bigger nodes at center
        forceAtlas2.assign(graph, {
          iterations: 100,
          settings: {
            gravity: 1,
            scalingRatio: 10,
            strongGravityMode: false,
            barnesHutOptimize: true,
            barnesHutTheta: 0.5,
            edgeWeightInfluence: 1,
          },
          // You can customize mass/size influence if needed here
        });

        // Kill previous Sigma instance if exists
        if (sigmaInstanceRef.current) sigmaInstanceRef.current.kill();

        // Initialize Sigma
        sigmaInstanceRef.current = new Sigma(graph, containerRef.current, {
          renderEdgeLabels: false,
          enableEdgeHoverEvents: true,
          edgeHoverColor: "edge",
          defaultEdgeColor: "#999",
          defaultNodeColor: "#0074D9",
          edgeHoverSizeRatio: 1.2,
          animationsTime: 1000,
        });
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

  if (error)
    return <div style={{ color: "red" }}>Error: {error}</div>;

  return (
    <div
      ref={containerRef}
      style={{ height: "90vh", width: "100%", border: "1px solid #ccc" }}
    />
  );
}
