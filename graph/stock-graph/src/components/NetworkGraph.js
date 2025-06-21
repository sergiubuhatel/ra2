import React, { useEffect, useRef, useState } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import { Sigma } from "sigma";
import chroma from "chroma-js";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const sigmaInstanceRef = useRef(null);
  const [error, setError] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  function hashStringToInt(str) {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash);
  }

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
        const graph = new Graph();

        const maxCentrality = Math.max(
          ...data.nodes.map((n) => n.eigenvector_centrality || 0)
        );

        const scaledSizes = data.nodes.map((node) => {
          const c = node.eigenvector_centrality || 0;
          return 5 + 20 * (c / maxCentrality);
        });
        const maxSize = Math.max(...scaledSizes);

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
            ...node, // keep all node stats
          });
        });

        const edgeColorScale = chroma
          .scale(["#ff7f7f", "#7f7fff", "#7fff7f", "#ffff7f", "#ff7fff"])
          .mode("lab");

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
              size: 0.5, // thinner lines
              color: edgeColorScale(t).hex(),
            });
          }
        });

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

        if (sigmaInstanceRef.current) sigmaInstanceRef.current.kill();

        const sigma = new Sigma(graph, containerRef.current, {
          renderEdgeLabels: false,
          enableEdgeHoverEvents: true,
          edgeColor: "default",
          edgeHoverColor: "edge",
          defaultEdgeColor: "#999",
          defaultNodeColor: "#0074D9",
          edgeHoverSizeRatio: 1.2,
          animationsTime: 1000,
        });

        sigmaInstanceRef.current = sigma;

        sigma.on("clickNode", ({ node }) => {
          const attrs = graph.getNodeAttributes(node);
          setSelectedNode(attrs);
        });

        sigma.on("clickStage", () => {
          setSelectedNode(null);
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

  return (
    <div style={{ display: "flex", height: "90vh" }}>
      <div
        ref={containerRef}
        style={{ flex: 3, border: "1px solid #ccc", position: "relative" }}
      />
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
        {selectedNode ? (
          <div>
            <p><strong>ID:</strong> {selectedNode.label}</p>
            <p><strong>Industry:</strong> {selectedNode.industry}</p>
            <p><strong>Eigenvector Centrality:</strong> {selectedNode.eigenvector_centrality?.toFixed(4)}</p>
            <p><strong>Betweenness Centrality:</strong> {selectedNode.betweenness_centrality?.toFixed(4)}</p>
            <p><strong>Closeness Centrality:</strong> {selectedNode.closeness_centrality?.toFixed(4)}</p>
            <p><strong>Degree Centrality:</strong> {selectedNode.degree_centrality?.toFixed(4)}</p>
          </div>
        ) : (
          <p>Click a node to view details</p>
        )}
      </div>
    </div>
  );
}
