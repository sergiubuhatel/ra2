import EdgeCurveProgram from "@sigma/edge-curve";
import { useEffect, useRef } from "react";
import { Sigma } from "sigma";

export default function useSigmaInstance(containerRef, graph, onNodeSelect) {
  const sigmaRef = useRef(null);

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
    
      defaultEdgeType: "curve",
      edgeProgramClasses: {
        curve: EdgeCurveProgram,
      }
    });

    sigmaRef.current = sigma;

    sigma.on("clickNode", ({ node }) => {
      const attrs = graph.getNodeAttributes(node);
      onNodeSelect(attrs);
    });

    sigma.on("clickStage", () => {
      onNodeSelect(null);
    });

    return () => {
      sigma.kill();
      sigmaRef.current = null;
    };
  }, [graph, containerRef, onNodeSelect]);
}
