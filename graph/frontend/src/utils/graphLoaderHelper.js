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
export function resolvePositionCollisions(pos, radius, placedNodes, padding = 3, maxAttempts = 100) {
  let collisionResolved = false;
  let attempts = 0;

  while (!collisionResolved && attempts < maxAttempts) {
    collisionResolved = true;

    for (const placedNode of placedNodes) {
      const dx = pos.x - placedNode.x;
      const dy = pos.y - placedNode.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const minDist = radius + placedNode.radius + padding;

      if (dist < minDist && dist > 0) {
        // push this node away to prevent overlap
        const overlap = minDist - dist;
        const angle = Math.atan2(dy, dx);

        pos.x += Math.cos(angle) * overlap;
        pos.y += Math.sin(angle) * overlap;

        collisionResolved = false;
        break; // check all placed nodes again after adjusting position
      }
    }

    attempts++;
  }

  return pos;
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

  graph.forEachEdge((edgeId, attributes) => {
    const weight = attributes.weight || 1;
    const thickness = mapWeightToThickness(weight, maxWeight);
    graph.setEdgeAttribute(edgeId, "size", thickness *0.2);
  });
}

// Generate color scale for edges
export const edgeColorScale = chroma
  .scale(["#ff7f7f", "#7f7fff", "#7fff7f", "#ffff7f", "#ff7fff"])
  .mode("lab");
