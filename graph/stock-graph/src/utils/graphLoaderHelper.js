// utils/graphLoaderHelper.js
import chroma from "chroma-js";

// Convert string to deterministic integer hash
export function hashStringToInt(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0; // Convert to 32bit integer
  }
  return Math.abs(hash);
}

// Position nodes based on size and outlier status
export function getPositionBySize(nodeId, size, maxSize, index, totalOutliers) {
  const normalizedSize = size / maxSize;
  const minRadius = 100;
  const maxRadius = 200;
  const outerRadius = 250;

  if (index !== -1 && totalOutliers > 0) {
    const angle = (2 * Math.PI * index) / totalOutliers;
    return {
      x: outerRadius * Math.cos(angle),
      y: outerRadius * Math.sin(angle),
    };
  } else {
    let radius = maxRadius - normalizedSize * (maxRadius - minRadius);
    if (radius > maxRadius) radius = maxRadius;
    const hash = hashStringToInt(nodeId);
    const angle = ((hash % 360) * Math.PI) / 180;
    return {
      x: radius * Math.cos(angle),
      y: radius * Math.sin(angle),
    };
  }
}

// Collision resolver to adjust node positions
export function resolveCollisions(graph) {
  const nodes = graph.nodes();
  const adjustedNodes = new Set();

  nodes.forEach((nodeId1) => {
    const { x: x1, y: y1, size: size1 } = graph.getNodeAttributes(nodeId1);
    nodes.forEach((nodeId2) => {
      if (nodeId1 !== nodeId2 && !adjustedNodes.has(nodeId2)) {
        const { x: x2, y: y2, size: size2 } = graph.getNodeAttributes(nodeId2);

        const dx = x2 - x1;
        const dy = y2 - y1;
        const distance = Math.sqrt(dx * dx + dy * dy);
        const minDistance = (size1 + size2) / 2;

        if (distance < minDistance) {
          const overlap = minDistance - distance;
          const angle = Math.atan2(dy, dx);
          const moveDistance = overlap / 2;
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

export function mapWeightToThickness(weight, maxWeight) {
  const minThickness = 1;
  const maxThickness = 25;

  if (maxWeight === 0) return minThickness; // avoid division by zero
  const normalized = weight / maxWeight;
  return minThickness + normalized * (maxThickness - minThickness);
}

export function getMaxEdgeWeight(graph) {
  let maxWeight = 0;
  graph.forEachEdge((_, attributes) => {
    const w = attributes.weight || 0;
    if (w > maxWeight) maxWeight = w;
  });
  return maxWeight === 0 ? 1 : maxWeight;  // avoid zero to prevent divide by zero
}

// Set edge thickness based on edge weight
export function setEdgeThickness(graph) {
  const maxWeight = getMaxEdgeWeight(graph);

  const minThickness = 1;
  const maxThickness = 25;

  graph.forEachEdge((edgeId, attributes) => {
    const weight = attributes.weight || 1;
    const thickness = mapWeightToThickness(weight, maxWeight);
    graph.setEdgeAttribute(edgeId, "size", thickness);
  });
}

// Generate color scale for edges
export const edgeColorScale = chroma
  .scale(["#ff7f7f", "#7f7fff", "#7fff7f", "#ffff7f", "#ff7fff"])
  .mode("lab");
