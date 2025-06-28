import Graph from "graphology";
import chroma from "chroma-js";
import forceAtlas2 from "graphology-layout-forceatlas2";
import {
  getPositionBySize,
  hashStringToInt,
  resolveCollisions,
  setEdgeThickness,
  edgeColorScale,
} from "./graphLoaderHelper";

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
  const sortedNodes = [...nodes].sort((a, b) => nodeSizes[a.id] - nodeSizes[b.id]);

  nodes.forEach(node => {
    const size = nodeSizes[node.id];
    const isOutlier = outlierSet.has(node.id);
    const outlierIndex = isOutlier
      ? sortedNodes.findIndex(n => n.id === node.id)
      : -1;

    const pos = getPositionBySize(node.id, size, maxSize, outlierIndex, outlierSet.size);
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
    });
  });
}

export function addEdgesToGraph(graph, edges) {
  edges.forEach((edge, i) => {
    const edgeId = `e${i}`;
    if (
      graph.hasNode(edge.source) &&
      graph.hasNode(edge.target) &&
      !graph.hasEdge(edge.source, edge.target)
    ) {
      const hash = hashStringToInt(edgeId);
      const t = (hash % 10000) / 10000;
      graph.addEdgeWithKey(edgeId, edge.source, edge.target, {
        size: 1,
        color: edgeColorScale(t).hex(),
      });
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

  resolveCollisions(graph);
  setEdgeThickness(graph);
}
