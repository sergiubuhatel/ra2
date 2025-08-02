import EdgeCurveProgram from "@sigma/edge-curve";
import { useEffect, useRef, useCallback } from "react";
import { Sigma } from "sigma";

export default function useSigmaInstance(containerRef, graph, onNodeSelect) {
  const sigmaRef = useRef(null);

  const simulateNodeClick = useCallback((nodeId) => {
    const sigma = sigmaRef.current;
    if (!sigma || !graph?.hasNode(nodeId)) return;

    const attrs = graph.getNodeAttributes(nodeId);
    onNodeSelect(attrs);

    // Highlight the node
    graph.setNodeAttribute(nodeId, "highlighted", true);

    // Remove highlight after 1 second
    setTimeout(() => {
      if (graph.hasNode(nodeId)) {
        graph.setNodeAttribute(nodeId, "highlighted", false);
        try {
          sigma.refresh();
        } catch {
        }
      }
    }, 1000);
  }, [graph, onNodeSelect]);

  useEffect(() => {
    if (!graph || !containerRef.current) return;

    if (sigmaRef.current) {
      sigmaRef.current.kill();
    }

    const sigma = new Sigma(graph, containerRef.current, {
      renderEdgeLabels: false,
      enableEdgeHoverEvents: true,
      edgeColor: "default",
      edgeHoverColor: "edge",
      defaultEdgeColor: "#999",
      defaultNodeColor: "#0074D9",
      edgeHoverSizeRatio: 1.2,
      animationsTime: 1000,
      labelSizeRatio: 0.5,
      labelRenderedSizeThreshold: 0,
      defaultEdgeType: "curve",
      edgeProgramClasses: {
        curve: EdgeCurveProgram,
      },
      // No need for nodeProgramClasses here, Sigma has circle built-in
      labelColor: { color: "gray" },
    });

    sigmaRef.current = sigma;

    sigma.on("clickNode", ({ node }) => {
      const attrs = graph.getNodeAttributes(node);
      onNodeSelect(attrs);
    });

    return () => {
      sigma.kill();
      sigmaRef.current = null;
    };
  }, [graph, containerRef, onNodeSelect]);

  return simulateNodeClick;
}
