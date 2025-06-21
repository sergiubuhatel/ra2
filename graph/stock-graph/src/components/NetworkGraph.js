import React, { useEffect, useRef, useState } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { Sigma } from "sigma";
import chroma from "chroma-js";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const sigmaInstanceRef = useRef(null);
  const [error, setError] = useState(null);

  // Simple deterministic hash function for strings -> positive int
  function hashStringToInt(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0; // Convert to 32bit int
    }
    return Math.abs(hash);
  }

  // Deterministic initial position on a ring based on node id hash
  function getDeterministicPosition(nodeId, index, total) {
    const hash = hashStringToInt(nodeId);
    const angle = ((hash % 360) * Math.PI) / 180; // degrees -> radians
    const radius = 10 + (index / total) * 20; // spread nodes on a ring between radius 10 and 30
    return {
      x: radius * Math.cos(angle),
      y: radius * Math.sin(angle),
    };
  }

  // Simple overlap reduction pass to avoid node overlaps
  function reduceOverlaps(graph, iterations = 5) {
    const nodes = graph.nodes();

    for (let iter = 0; iter < iterations; iter++) {
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const n1 = nodes[i];
          const n2 = nodes[j];
          const pos1 = graph.getNodeAttributes(n1);
          const pos2 = graph.getNodeAttributes(n2);

          const dx = pos2.x - pos1.x;
          const dy = pos2.y - pos1.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          const minDist = (pos1.size + pos2.size) * 1.2; // minimum distance to avoid overlap

          if (dist > 0 && dist < minDist) {
            const overlap = (minDist - dist) / 2;
            const offsetX = (dx / dist) * overlap;
            const offsetY = (dy / dist) * overlap;

            graph.setNodeAttribute(n1, "x", pos1.x - offsetX);
            graph.setNodeAttribute(n1, "y", pos1.y - offsetY);
            graph.setNodeAttribute(n2, "x", pos2.x + offsetX);
            graph.setNodeAttribute(n2, "y", pos2.y + offsetY);
          }
        }
      }
    }
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

        // Add nodes with deterministic positions & size/color based on centrality
        data.nodes.forEach((node, index) => {
          const centrality = node.eigenvector_centrality || 0;
          const scaledSize = 5 + 20 * (centrality / maxCentrality);
          const scaledColor = chroma
            .scale(["#b0d0ff", "#003399"])
            .mode("lab")(centrality / maxCentrality)
            .hex();

          const pos = getDeterministicPosition(node.id, index, data.nodes.length);

          graph.addNode(node.id, {
            label: node.label,
            industry: node.industry,
            size: scaledSize,
            color: scaledColor,
            x: pos.x,
            y: pos.y,
            mass: scaledSize,
          });
        });

        // Create a color scale for edges
        const edgeColorScale = chroma
          .scale(["#ff7f7f", "#7f7fff", "#7fff7f"])
          .mode("lab");

        // Add edges with deterministic colors based on edge ID
        data.edges.forEach((edge, i) => {
          const edgeId = `e${i}`;
          if (
            graph.hasNode(edge.source) &&
            graph.hasNode(edge.target) &&
            !graph.hasEdge(edge.source, edge.target)
          ) {
            const hash = hashStringToInt(edgeId);
            const t = (hash % 10000) / 10000; // Normalize to [0,1]

            graph.addEdgeWithKey(edgeId, edge.source, edge.target, {
              size: Math.log((edge.weight || 1) + 1),
              color: edgeColorScale(t).hex(),
            });
          }
        });

        // Run ForceAtlas2 layout with strong gravity and higher scalingRatio for better spacing
        forceAtlas2.assign(graph, {
          iterations: 200,
          settings: {
            gravity: 5,
            strongGravityMode: true,
            scalingRatio: 15,
            barnesHutOptimize: true,
            barnesHutTheta: 0.5,
            edgeWeightInfluence: 1,
          },
        });

        // Reduce node overlaps after layout
        reduceOverlaps(graph);

        // Kill previous Sigma instance if exists
        if (sigmaInstanceRef.current) sigmaInstanceRef.current.kill();

        // Initialize Sigma with edge colors from graph attributes
        sigmaInstanceRef.current = new Sigma(graph, containerRef.current, {
          renderEdgeLabels: false,
          enableEdgeHoverEvents: true,
          edgeColor: "default",  // Use edge.color attribute
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
