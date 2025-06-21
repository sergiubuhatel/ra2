import React, { useState, useEffect } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import chroma from "chroma-js";

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
      const graph = new Graph();

      const maxCentrality = Math.max(
        ...fileContent.nodes.map((n) => n.eigenvector_centrality || 0)
      );

      // Calculate node sizes and keep track per industry
      const industrySizes = {};
      const nodeSizes = {};
      fileContent.nodes.forEach((node) => {
        const c = node.eigenvector_centrality || 0;
        const scaledSize = 5 + 20 * (c / maxCentrality);
        nodeSizes[node.id] = scaledSize;
        const industry = node.industry || "unknown";
        if (!industrySizes[industry]) industrySizes[industry] = [];
        industrySizes[industry].push(scaledSize);
      });

      // Compute average size per industry
      const industryAvgSize = Object.entries(industrySizes).map(([industry, sizes]) => {
        const avg = sizes.reduce((a, b) => a + b, 0) / sizes.length;
        return { industry, avgSize: avg };
      });

      // Sort industries descending by avgSize
      industryAvgSize.sort((a, b) => b.avgSize - a.avgSize);

      // Assign colors:
      // Top 3 industries get fixed colors blue, green, yellow
      // Others get colors from chroma Set2 scale
      const fixedColors = ["#0074D9", "#2ECC40", "#FFDC00"]; // blue, green, yellow
      const industryColorMap = {};
      const palette = chroma.scale("Set2").mode("lab");

      industryAvgSize.forEach(({ industry }, idx) => {
        if (idx < 3) {
          industryColorMap[industry] = fixedColors[idx];
        } else {
          // Spread out other colors across palette
          industryColorMap[industry] = palette((idx - 3) / Math.max(1, industryAvgSize.length - 3)).hex();
        }
      });

      // Add nodes with assigned color per industry
      fileContent.nodes.forEach((node) => {
        const centrality = node.eigenvector_centrality || 0;
        const scaledSize = 5 + 20 * (centrality / maxCentrality);
        const color = industryColorMap[node.industry || "unknown"];
        const pos = getPositionBySize(node.id, scaledSize, 25 + 20); // maxSize approx

        graph.addNode(node.id, {
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

      const edgeColorScale = chroma
        .scale(["#ff7f7f", "#7f7fff", "#7fff7f", "#ffff7f", "#ff7fff"])
        .mode("lab");

      fileContent.edges.forEach((edge, i) => {
        const edgeId = `e${i}`;
        if (
          graph.hasNode(edge.source) &&
          graph.hasNode(edge.target) &&
          !graph.hasEdge(edge.source, edge.target)
        ) {
          const hash = hashStringToInt(edgeId);
          const t = (hash % 10000) / 10000;
          graph.addEdgeWithKey(edgeId, edge.source, edge.target, {
            size: 0.5,
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

      setGraph(graph);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setGraph(null);
    }
  }, [fileContent]);

  return { graph, error };
}
