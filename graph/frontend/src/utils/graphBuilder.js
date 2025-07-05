import Graph from "graphology";
import chroma from "chroma-js";
import forceAtlas2 from "graphology-layout-forceatlas2";
import {
  getPositionBySize,
  hashStringToInt,
  resolvePositionCollisions,
  setEdgeThickness,
  edgeColorScale,
  mapWeightToThickness,
  } from "./graphLoaderHelper";
import {getDeterministicColor, hexToRgba, blendWithBlack } from "../utils/colors";

export function calculateNodeSizes(nodes, factor) {
  const maxCentrality = Math.max(...nodes.map(n => n.eigenvector_centrality || 0));
  const sizes = {};
  nodes.forEach(n => {
    const c = n.eigenvector_centrality || 0;
    sizes[n.id] = 5 + factor * (c / maxCentrality);
  });
  return sizes;
}

export function identifyOutliers(nodes, nodeSizes) {
  const sorted = [...nodes].sort((a, b) => nodeSizes[a.id] - nodeSizes[b.id]);
  const count = Math.floor(sorted.length * 0.1);
  return new Set(sorted.slice(0, count).map(n => n.id));
}

export function assignNodeAttributes(graph, nodes, nodeSizes, outlierSet, industryColors) {
  const maxSize = Math.max(...Object.values(nodeSizes));
  const sortedNodes = [...nodes].sort((a, b) => nodeSizes[b.id] - nodeSizes[a.id]);

  const placed = [];
  const spiralSpacing = 50;
  const angleIncrement = 0.6;
  const baseOffset = 1; // Ensures even smallest node has some spacing

  sortedNodes.forEach((node, index) => {
    const size = nodeSizes[node.id];
    const radius = size / 2;

    // Spiral radius grows with size and index
    const angle = angleIncrement * index;
    const spiralRadius = spiralSpacing * (baseOffset + size / maxSize + Math.sqrt(index));

    let pos = {
      x: spiralRadius * Math.cos(angle),
      y: spiralRadius * Math.sin(angle),
    };

    pos = resolvePositionCollisions(pos, radius, placed);

    placed.push({ x: pos.x, y: pos.y, radius });

    const color = industryColors[node.industry]
      || chroma.scale(["#b0d0ff", "#003399"]).mode("lab")(size / maxSize).hex();

    graph.addNode(node.id, {
      ...node,
      size,
      color,
      x: pos.x,
      y: pos.y,
      mass: size,
      initialPosition: pos,
      labelColor: "#ffffff"
    });
  });
}

export function getMaxEdgeWeight(edges) {
  let maxWeight = 0;

  edges.forEach((edge) => {
    const w = edge.weight || 0;
    if (w > maxWeight) maxWeight = w;
  });

  return maxWeight === 0 ? 1 : maxWeight;
}

export function addEdgesToGraph(graph, edges, edgeThickness) {
  const maxWeight = getMaxEdgeWeight(edges);

  // Sort edges by weight ASCENDING so heavier ones are added LAST
  const sortedEdges = [...edges].sort((a, b) => (a.weight || 0.1) - (b.weight || 0.1));

  sortedEdges.forEach((edge, i) => {
    const edgeId = `e${i}`;
    if (
      graph.hasNode(edge.source) &&
      graph.hasNode(edge.target) &&
      !graph.hasEdge(edge.source, edge.target)
    ) {
      const hash = hashStringToInt(edgeId);
      const t = (hash % 10000) / 10000;
      const weight = edge.weight || 0.1;

      const thickness = mapWeightToThickness(weight, maxWeight);
      if (thickness > edgeThickness) {
        const baseColor = getDeterministicColor(t);
        const weightRatio = weight / maxWeight;

        const fadedColor = blendWithBlack(baseColor, (1 - weightRatio) * 0.9);

        graph.addEdgeWithKey(edgeId, edge.source, edge.target, {
          weight: weight,
          color: fadedColor,
          size: thickness, // use `size` for edge width if needed
          curvature: 0.25,
        });
      }
    }
  });
}

export function runLayoutAndPostProcessing(graph) {
  forceAtlas2.assign(graph, {
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

  //resolveCollisions(graph);
  setEdgeThickness(graph);
}
