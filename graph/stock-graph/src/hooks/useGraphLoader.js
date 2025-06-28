import { useState, useEffect } from "react";
import Graph from "graphology";
import forceAtlas2 from "graphology-layout-forceatlas2";
import chroma from "chroma-js"; 

import {
  hashStringToInt,
  getPositionBySize,
  resolveCollisions,
  setEdgeThickness,
  edgeColorScale,
} from "../utils/graphLoaderHelper";

export default function useGraphLoader(fileContent = null, industryColors = {}, nodeSizeFactor = 20) {
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
        const scaledSize = 5 + nodeSizeFactor * (centrality / maxCentrality);
        nodeSizes[node.id] = scaledSize;
      });

      const maxSize = Math.max(...Object.values(nodeSizes));

      // Define outliers as the smallest 10% nodes
      const sortedNodes = [...fileContent.nodes].sort(
        (a, b) => nodeSizes[a.id] - nodeSizes[b.id]
      );
      const outlierCount = Math.floor(sortedNodes.length * 0.1);
      const outlierSet = new Set(sortedNodes.slice(0, outlierCount).map(n => n.id));

      // Add nodes with positions and color by industry
      fileContent.nodes.forEach((node) => {
        const scaledSize = nodeSizes[node.id];
        const isOutlier = outlierSet.has(node.id);
        const outlierIndex = isOutlier
          ? sortedNodes.slice(0, outlierCount).findIndex((n) => n.id === node.id)
          : -1;

        const pos = getPositionBySize(
          node.id,
          scaledSize,
          maxSize,
          outlierIndex,
          outlierCount
        );

        const color = industryColors[node.industry]
          ? industryColors[node.industry]
          : chroma.scale(["#b0d0ff", "#003399"])
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
          initialPosition: { x: pos.x, y: pos.y },
          ...node,
        });
      });

      // Add edges with default style
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
            size: 1,
            color: edgeColorScale(t).hex(),
          });
        }
      });

      // Run ForceAtlas2 layout with enhanced separation
      forceAtlas2.assign(g, {
        iterations: 500,
        settings: {
          gravity: 5,
          scalingRatio: 10,
          strongGravityMode: true,
          barnesHutOptimize: true,
          barnesHutTheta: 0.5,
          edgeWeightInfluence: 1.2,
          outboundAttractionDistribution: true,
        },
      });

      // Resolve collisions
      resolveCollisions(g);

      // Set edge thickness
      setEdgeThickness(g);

      setGraph(g);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setGraph(null);
    }
  }, [fileContent, industryColors, nodeSizeFactor]);

  // Return graph with fixed node positions
  const getUpdatedGraph = () => {
    if (graph) {
      graph.forEachNode((nodeId, attributes) => {
        if (attributes.initialPosition) {
          graph.setNodeAttribute(nodeId, 'x', attributes.initialPosition.x);
          graph.setNodeAttribute(nodeId, 'y', attributes.initialPosition.y);
        }
      });
    }
    return graph;
  };

  return { graph: getUpdatedGraph(), error };
}
