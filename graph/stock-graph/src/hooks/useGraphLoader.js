import { useState, useEffect } from "react";
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
 * Positions nodes such that larger nodes are closer to the center,
 * and smaller nodes are placed further away.
 */
function getPositionBySize(nodeId, size, maxSize, index, totalOutliers) {
  const normalizedSize = size / maxSize;

  // Define inner node placement ranges (minimum and maximum radius)
  const minRadius = 100; // Minimum distance from the center for larger nodes
  const maxRadius = 300; // Maximum distance for smaller nodes

  // Calculate radial distance: larger nodes are closer to center
  const radius = minRadius + (maxRadius - minRadius) * (1 - normalizedSize); // Inverse relationship

  const outerRadius = 350; // Set a fixed outer radius for outliers (smallest nodes)
  if (index !== -1 && totalOutliers > 0) {
    const angle = (2 * Math.PI * index) / totalOutliers;
    return {
      x: outerRadius * Math.cos(angle),
      y: outerRadius * Math.sin(angle),
    };
  }

  const hash = hashStringToInt(nodeId);
  const angle = ((hash % 360) * Math.PI) / 180; // Distribute nodes based on hash

  return {
    x: radius * Math.cos(angle),
    y: radius * Math.sin(angle),
  };
}

/**
 * Resolves collisions by ensuring nodes only touch each other, no overlap.
 */
function resolveCollisions(graph) {
  const nodes = graph.nodes();

  // For each pair of nodes, check if they are overlapping and adjust positions
  nodes.forEach((nodeId1) => {
    const { x: x1, y: y1, size: size1 } = graph.getNodeAttributes(nodeId1);
    nodes.forEach((nodeId2) => {
      if (nodeId1 !== nodeId2) {
        const { x: x2, y: y2, size: size2 } = graph.getNodeAttributes(nodeId2);

        // Calculate the distance between the two nodes
        const dx = x2 - x1;
        const dy = y2 - y1;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const minDistance = (size1 + size2) / 2;

        // If nodes overlap, adjust their positions so they just touch
        if (distance < minDistance) {
          const overlap = minDistance - distance;
          const angle = Math.atan2(dy, dx);

          // Move nodes apart so they just touch each other
          const moveDistance = overlap / 2; // Split the overlap equally
          graph.setNodeAttribute(nodeId1, 'x', x1 - moveDistance * Math.cos(angle));
          graph.setNodeAttribute(nodeId1, 'y', y1 - moveDistance * Math.sin(angle));
          graph.setNodeAttribute(nodeId2, 'x', x2 + moveDistance * Math.cos(angle));
          graph.setNodeAttribute(nodeId2, 'y', y2 + moveDistance * Math.sin(angle));
        }
      }
    });
  });
}

/**
 * Sets edge thickness based on the sizes of connected nodes.
 */
function setEdgeThickness(graph) {
  graph.forEachEdge((edgeId, attributes) => {
    const source = attributes.source;
    const target = attributes.target;

    // Check if the nodes exist before accessing their attributes
    if (graph.hasNode(source) && graph.hasNode(target)) {
      const sizeSource = graph.getNodeAttributes(source).size;
      const sizeTarget = graph.getNodeAttributes(target).size;

      // Set edge thickness based on the sum of the connected nodes' sizes
      const edgeThickness = Math.min((sizeSource + sizeTarget) / 10, 10); // Cap the max edge thickness
      graph.setEdgeAttribute(edgeId, 'size', edgeThickness);
    }
  });
}

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
        const scaledSize = 5 + nodeSizeFactor * (centrality / maxCentrality); // Default smaller size
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

        // Use industryColors if available, else fallback to blue scale by size
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
            size: 1, // Default edge thickness
            color: edgeColorScale(t).hex(),
          });
        }
      });

      // Run ForceAtlas2 layout for better separation
      forceAtlas2.assign(g, {
        iterations: 500,  // Increased iterations for better stability
        settings: {
          gravity: 5,  // Increased gravity to pull nodes apart more
          scalingRatio: 10,  // Increased scaling ratio for more space
          strongGravityMode: true,
          barnesHutOptimize: true,
          barnesHutTheta: 0.5,
          edgeWeightInfluence: 1.2,  // Increased edge weight influence
          outboundAttractionDistribution: true,
        },
      });

      // Resolve collisions after layout
      resolveCollisions(g);

      // Set edge thickness based on node sizes
      setEdgeThickness(g);

      setGraph(g);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setGraph(null);
    }
  }, [fileContent, industryColors, nodeSizeFactor]);

  // Make sure to return the graph with positions intact
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
