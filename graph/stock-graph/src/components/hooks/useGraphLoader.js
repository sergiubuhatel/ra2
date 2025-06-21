import React, { useState, useEffect } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import chroma from "chroma-js";

// Helper to convert string to integer hash
function hashStringToInt(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0; // Convert to 32bit integer
  }
  return Math.abs(hash);
}

/**
 * Positions nodes so bigger nodes are closer to center.
 * Outliers placed evenly on same outer circle.
 */
function getPositionBySize(nodeId, size, maxSize, index, totalOutliers) {
  const normalizedSize = size / maxSize;
  const minRadius = 5;
  const maxRadius = 50;
  const outerRadius = 60;

  // radius inversely proportional to size: bigger nodes closer in
  let radius = maxRadius - normalizedSize * (maxRadius - minRadius);

  // Outlier detection: if radius would be bigger than maxRadius (unlikely here), place on outer circle
  if (radius > maxRadius) radius = maxRadius;

  // If node is an outlier (defined externally), place evenly on outer circle
  if (index !== -1 && totalOutliers > 0) {
    const angle = (2 * Math.PI * index) / totalOutliers;
    return {
      x: outerRadius * Math.cos(angle),
      y: outerRadius * Math.sin(angle),
    };
  } else {
    // Distribute inner nodes by hashing id for angle
    const hash = hashStringToInt(nodeId);
    const angle = ((hash % 360) * Math.PI) / 180;
    return {
      x: radius * Math.cos(angle),
      y: radius * Math.sin(angle),
    };
  }
}

export default function useGraphLoader(fileContent = null) {
  const [graph, setGraph] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!fileContent) {
      setGraph(null);
      setError(null);
      return;
    }

    try {
      const g = new Graph();

      // Find max centrality to scale sizes
      const maxCentrality = Math.max(
        ...fileContent.nodes.map((n) => n.eigenvector_centrality || 0)
      );

      // Calculate scaled sizes for each node
      const nodeSizes = {};
      fileContent.nodes.forEach((node) => {
        const centrality = node.eigenvector_centrality || 0;
        const scaledSize = 5 + 20 * (centrality / maxCentrality);
        nodeSizes[node.id] = scaledSize;
      });

      const maxSize = Math.max(...Object.values(nodeSizes));

      // Define outliers as the smallest 10% nodes (or you can tweak this)
      const sortedNodes = [...fileContent.nodes].sort(
        (a, b) => nodeSizes[a.id] - nodeSizes[b.id]
      );
      const outlierCount = Math.floor(sortedNodes.length * 0.1);
      const outlierSet = new Set(sortedNodes.slice(0, outlierCount).map(n => n.id));

      // Add nodes with positions
      fileContent.nodes.forEach((node) => {
        const scaledSize = nodeSizes[node.id];

        const isOutlier = outlierSet.has(node.id);
        // If outlier, index among outliers for angle calculation, else -1
        const outlierIndex = isOutlier
          ? sortedNodes
              .slice(0, outlierCount)
              .findIndex((n) => n.id === node.id)
          : -1;

        const pos = getPositionBySize(
          node.id,
          scaledSize,
          maxSize,
          outlierIndex,
          outlierCount
        );

        // Color scale for nodes (blue gradient)
        const color = chroma
          .scale(["#b0d0ff", "#003399"])
          .mode("lab")(scaledSize / maxSize)
          .hex();

        g.addNode(node.id, {
          label: node.label,
          industry: node.industry,
          size: scaledSize,
          color,
          x: pos.x,
          y: pos.y,
          mass: scaledSize,
          ...node,
        });
      });

      // Add edges with default style
      const edgeColorScale = chroma
        .scale(["#ff7f7f", "#7f7fff", "#7fff7f", "#ffff7f", "#ff7fff"])
        .mode("lab");

      fileContent.edges.forEach((edge, i) => {
        const edgeId = `e${i}`;
        if (
          g.hasNode(edge.source) &&
          g.hasNode(edge.target) &&
          !g.hasEdge(edge.source, edge.target)
        ) {
          const hash = hashStringToInt(edgeId);
          const t = (hash % 10000) / 10000;
          g.addEdgeWithKey(edgeId, edge.source, edge.target, {
            size: 0.5,
            color: edgeColorScale(t).hex(),
          });
        }
      });

      // Run ForceAtlas2 layout for better arrangement
      forceAtlas2.assign(g, {
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

      setGraph(g);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setGraph(null);
    }
  }, [fileContent]);

  return { graph, error };
}
