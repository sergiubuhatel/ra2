import EdgeCurveProgram from "@sigma/edge-curve";
import { useEffect, useRef } from "react";
import { Sigma } from "sigma";

export default function useSigmaInstance(containerRef, graph, onNodeSelect) {
  const sigmaRef = useRef(null);

  // ✅ Expose this function to trigger click
  const simulateNodeClick = (nodeId) => {
    if (!sigmaRef.current || !graph.hasNode(nodeId)) return;

    const attrs = graph.getNodeAttributes(nodeId);
    onNodeSelect(attrs);

    // Optionally highlight the node in the renderer:
    sigmaRef.current.getCamera().animate(graph.getNodeAttributes(nodeId), {
      duration: 600
    });

    // Optional: visually highlight the node (manually track selection state)
    graph.setNodeAttribute(nodeId, 'highlighted', true);
    sigmaRef.current.refresh();
  };

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
