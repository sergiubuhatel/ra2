import React, { useEffect, useRef, useState } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { Sigma } from "sigma";
import chroma from "chroma-js";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const sigmaInstanceRef = useRef(null);
  const [error, setError] = useState(null);

  // Deterministic hash function for string -> positive int
  function hashStringToInt(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash);
  }

  // Deterministic node placement function
  function getPositionBySize(nodeId, size, maxSize) {
    const hash = hashStringToInt(nodeId);
    const angle = ((hash % 360) * Math.PI) / 180;

    const minRadius = 5;
    const maxRadius = 40;

    const normalizedSize = size / maxSize;
    const radius = minRadius + (1 - normalizedSize) * (maxRadius - minRadius);

    return {
      x: radius * Math.cos(angle),
      y: radius * Math.sin(angle),
    };
  }

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

        const scaledSizes = data.nodes.map((node) => {
          const c = node.eigenvector_centrality || 0;
          return 5 + 20 * (c / maxCentrality);
        });
        const maxSize = Math.max(...scaledSizes);

        // Add nodes
        data.nodes.forEach((node) => {
          const centrality = node.eigenvector_centrality || 0;
          const scaledSize = 5 + 20 * (centrality / maxCentrality);
          const color = chroma
            .scale(["#b0d0ff", "#003399"])
            .mode("lab")(centrality / maxCentrality)
            .hex();

          const pos = getPositionBySize(node.id, scaledSize, maxSize);

          graph.addNode(node.id, {
            label: node.label,
            industry: node.industry,
            size: scaledSize,
            color,
            x: pos.x,
            y: pos.y,
            mass: scaledSize,
          });
        });

        // Create colorful edge scale
        const edgeColorScale = chroma
          .scale(["#ff7f7f", "#7f7fff", "#7fff7f", "#ffff7f", "#ff7fff"])
          .mode("lab");

        // Add edges with diverse colors and thinner size
        data.edges.forEach((edge, i) => {
          const edgeId = `e${i}`;
          if (
            graph.hasNode(edge.source) &&
            graph.hasNode(edge.target) &&
            !graph.hasEdge(edge.source, edge.target)
          ) {
            const hash = hashStringToInt(edgeId);
            const t = (hash % 10000) / 10000;

            graph.addEdgeWithKey(edgeId, edge.source, edge.target, {
              size: 0.5, // thinner edges
              color: edgeColorScale(t).hex(),
            });
          }
        });

        // Small layout pass to reduce overlap
        forceAtlas2.assign(graph, {
          iterations: 50,
          settings: {
            gravity: 5,
            scalingRatio: 10,
            strongGravityMode: true,
            barnesHutOptimize: true,
            barnesHutTheta: 0.5,
            edgeWeightInfluence: 1,
          },
        });

        // Clean previous Sigma instance
        if (sigmaInstanceRef.current) sigmaInstanceRef.current.kill();

        // Initialize Sigma
        sigmaInstanceRef.current = new Sigma(graph, containerRef.current, {
          renderEdgeLabels: false,
          enableEdgeHoverEvents: true,
          edgeColor: "default", // use color from edge.color
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
