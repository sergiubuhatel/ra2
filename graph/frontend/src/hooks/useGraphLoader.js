import { useState, useEffect } from "react";
import Graph from "graphology";
import {
  calculateNodeSizes,
  identifyOutliers,
  assignNodeAttributes,
  addEdgesToGraph,
  runLayoutAndPostProcessing,
} from "../utils/graphBuilder";

export default function useGraphLoader(fileContent = null, industryColors = {}, edgeThickness, nodeSizeFactor = 20) {
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

      const nodeSizes = calculateNodeSizes(fileContent.nodes, nodeSizeFactor);
      const outlierSet = identifyOutliers(fileContent.nodes, nodeSizes);

      assignNodeAttributes(g, fileContent.nodes, nodeSizes, outlierSet, industryColors);
      addEdgesToGraph(g, fileContent.edges, edgeThickness);
      runLayoutAndPostProcessing(g);

      setGraph(g);
      setError(null);
    } catch (err) {
      console.error(err);
      setError(err.message);
      setGraph(null);
    }
  }, [fileContent, industryColors, nodeSizeFactor, edgeThickness]);

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
