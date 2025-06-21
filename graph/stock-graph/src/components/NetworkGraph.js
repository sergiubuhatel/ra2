import React, { useRef, useState } from "react";
import NodeInfoPanel from "./NodeInfoPanel";
import useGraphLoader from "./hooks/useGraphLoader";
import useSigmaInstance from "./hooks/useSigmaInstance";

export default function NetworkGraph() {
  const containerRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);

  const { graph, error } = useGraphLoader();
  useSigmaInstance(containerRef, graph, setSelectedNode);

  if (error) {
    return <div style={{ color: "red" }}>Error: {error}</div>;
  }

  return (
    <div style={{ display: "flex", height: "90vh" }}>
      <div
        ref={containerRef}
        style={{ flex: 3, border: "1px solid #ccc", position: "relative" }}
      />
      <NodeInfoPanel node={selectedNode} />
    </div>
  );
}
