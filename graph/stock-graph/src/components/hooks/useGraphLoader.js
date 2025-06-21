import { useEffect, useState } from "react";
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

export default function useGraphLoader() {
  const [graph, setGraph] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch("/graph_with_centrality.json")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load graph data");
        return res.json();
      })
      .then((data) => {
        const graph = new Graph();

        const maxCentrality = Math.max(
          ...data.nodes.map((n) => n.eigenvector_centrality || 0)
        );

        const scaledSizes = data.nodes.map((node) => {
          const c = node.eigenvector_centrality || 0;
          return 5 + 20 * (c / maxCentrality);
        });
        const maxSize = Math.max(...scaledSizes);

        data.nodes.forEach((node) => {
          const centrality = node.eigenvector_centrality || 0;
          const scaledSize = 5 + 20 * (centrality / maxCentrality);
          const color = chroma
            .scale(["#b0d0ff", "#003399"])
            .mode("lab")(centrality / maxCentrality)
            .hex();
          const pos = getPositionBySize(node.id, scaledSize, maxSize);

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

        data.edges.forEach((edge, i) => {
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
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
      });

    return () => {
      setGraph(null);
    };
  }, []);

  return { graph, error };
}
