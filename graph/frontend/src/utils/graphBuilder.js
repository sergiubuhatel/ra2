import chroma from "chroma-js";
import forceAtlas2 from "graphology-layout-forceatlas2";
import {
  hashStringToInt,
  resolvePositionCollisions,
  setEdgeThickness,
  mapWeightToThickness,
  } from "./graphLoaderHelper";
import {getDeterministicColor, blendWithBlack } from "../utils/colors";

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
  const baseOffset = 1;

  sortedNodes.forEach((node, index) => {
    const size = nodeSizes[node.id];
    const radius = size / 2;

    let pos;

    if (index === 0) {
      // Largest node at the center
      pos = { x: 0, y: 0 };
    } else {
      const angle = angleIncrement * index;
      const spiralRadius = spiralSpacing * (baseOffset + size / maxSize + Math.sqrt(index));
      pos = {
        x: spiralRadius * Math.cos(angle),
        y: spiralRadius * Math.sin(angle),
      };

      // Resolve collisions with already-placed nodes
      pos = resolvePositionCollisions(pos, radius, placed);
    }

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
      //labelColor: "#ffffff",
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

  const sortedEdges = [...edges].sort((a, b) => (a.weight || 0.1) - (b.weight || 0.1));

  sortedEdges.forEach((edge, i) => {
    const edgeId = `e${i}`;
    const { source, target, weight = 0.1 } = edge;

    if (
      graph.hasNode(source) &&
      graph.hasNode(target) &&
      !graph.hasEdge(source, target)
    ) {
      const sourceNode = graph.getNodeAttributes(source);
      const targetNode = graph.getNodeAttributes(target);

      const sourceCentrality = sourceNode.eigenvector_centrality || 0;
      const targetCentrality = targetNode.eigenvector_centrality || 0;

      const highNode = sourceCentrality >= targetCentrality ? sourceNode : targetNode;
      const lowCentrality = Math.min(sourceCentrality, targetCentrality);

      const thickness = mapWeightToThickness(weight, maxWeight);

      if (thickness > edgeThickness) {
        // Fade based on how low the lower centrality is (range: 0.0 - 1.0)
        const fadeStrength = 1 - lowCentrality; // lower centrality = more fade
        const fadedColor = blendWithBlack(highNode.color, fadeStrength * 0.75);

        graph.addEdgeWithKey(edgeId, source, target, {
          weight,
          color: fadedColor,
          size: thickness,
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
