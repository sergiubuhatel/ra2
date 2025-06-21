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
 * Positions nodes so bigger nodes are closer to the center.
 * Outliers placed evenly on the outer circle.
 */
function getPositionBySize(nodeId, size, maxSize, index, totalOutliers) {
  const normalizedSize = size / maxSize;
  const minRadius = 100; // Minimum radius for inner nodes
  const maxRadius = 200; // Maximum radius for inner nodes
  const outerRadius = 250; // Fixed outer radius for outliers (same for all outer nodes)
  
  // If node is an outlier (defined externally), place it evenly on the outer circle
  if (index !== -1 && totalOutliers > 0) {
    const angle = (2 * Math.PI * index) / totalOutliers;
    return {
      x: outerRadius * Math.cos(angle),
      y: outerRadius * Math.sin(angle),
    };
  } else {
    // For inner nodes, place them based on their size
    let radius = maxRadius - normalizedSize * (maxRadius - minRadius);
    if (radius > maxRadius) radius = maxRadius;

    // Distribute inner nodes by hashing id for angle
    const hash = hashStringToInt(nodeId);
    const angle = ((hash % 360) * Math.PI) / 180;
    
    // Larger nodes move closer to the center
    const centerPull = Math.max(50, 1 - normalizedSize);  // Pull larger nodes toward center

    return {
      x: (radius * centerPull) * Math.cos(angle),
      y: (radius * centerPull) * Math.sin(angle),
    };
  }
}

/**
 * Checks for node collisions and adjusts positions if they overlap
 */
function resolveCollisions(graph, iterations = 10) {
  const nodes = graph.nodes();

  // Iterative resolution of collisions
  for (let i = 0; i < iterations; i++) {
    const adjustedNodes = new Set();

    nodes.forEach((nodeId1) => {
      const { x: x1, y: y1, size: size1 } = graph.getNodeAttributes(nodeId1);
      nodes.forEach((nodeId2) => {
        if (nodeId1 !== nodeId2 && !adjustedNodes.has(nodeId2)) {
          const { x: x2, y: y2, size: size2 } = graph.getNodeAttributes(nodeId2);
          
          // Calculate distance between nodes
          const dx = x2 - x1;
          const dy = y2 - y1;
          const distance = Math.sqrt(dx * dx + dy * dy);
          const minDistance = (size1 + size2) / 2 + 10; // Buffer distance

          // If nodes overlap, move them apart
          if (distance < minDistance) {
            const overlap = minDistance - distance;
            const angle = Math.atan2(dy, dx);

            // Move nodes apart in the direction of the angle
            const moveDistance = overlap / 2; // Split overlap equally
            graph.setNodeAttribute(nodeId1, 'x', x1 - moveDistance * Math.cos(angle));
            graph.setNodeAttribute(nodeId1, 'y', y1 - moveDistance * Math.sin(angle));
            graph.setNodeAttribute(nodeId2, 'x', x2 + moveDistance * Math.cos(angle));
            graph.setNodeAttribute(nodeId2, 'y', y2 + moveDistance * Math.sin(angle));
          }
        }
      });

      adjustedNodes.add(nodeId1);
    });
  }
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

        // Use the original position calculation without depending on size
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
          // Store initial positions so they don't change
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
            size: 0.5,
            color: edgeColorScale(t).hex(),
          });
        }
      });

      // Run ForceAtlas2 layout with enhanced separation
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
      // Make sure the node positions remain fixed
      graph.forEachNode((nodeId, attributes) => {
        // Restore the initial positions
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
