import React, { useState, useEffect, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import * as d3 from "d3-force";

export default function GraphViewer() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [layout, setLayout] = useState("forceAtlas2");
  const fgRef = useRef();

  // Load graph data once
  useEffect(() => {
    fetch("/graph_top_50.json")
      .then(res => res.json())
      .then(data => {
        const links = data.edges.map(e => ({
          source: e.source,
          target: e.target,
          value: e.weight
        }));
        setGraphData({ nodes: data.nodes, links });
      });
  }, []);

  // Apply layout when layout or nodes change
  useEffect(() => {
    if (!graphData.nodes.length) return;

    // Clone nodes so we don't mutate original state
    let newNodes = graphData.nodes.map(node => ({ ...node }));
    let newLinks = graphData.links;

    if (layout === "random") {
      newNodes.forEach(node => {
        node.x = Math.random() * 800;
        node.y = Math.random() * 600;
        // Clear velocities to avoid simulation issues
        delete node.vx;
        delete node.vy;
      });
      setGraphData({ nodes: newNodes, links: newLinks });
    }
    else if (layout === "circular") {
      const radius = 300;
      newNodes.forEach((node, i) => {
        const angle = (i / newNodes.length) * 2 * Math.PI;
        node.x = radius * Math.cos(angle);
        node.y = radius * Math.sin(angle);
        delete node.vx;
        delete node.vy;
      });
      setGraphData({ nodes: newNodes, links: newLinks });
    }
    else if (layout === "fruchterman") {
      const sim = d3.forceSimulation(newNodes)
        .force("link", d3.forceLink(newLinks).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-150))
        .force("center", d3.forceCenter(0, 0));

      sim.force("link").links(newLinks);

      // Reset velocities
      newNodes.forEach(node => {
        node.vx = 0;
        node.vy = 0;
      });

      sim.stop();
      for (let i = 0; i < 300; i++) sim.tick();

      setGraphData({ nodes: newNodes, links: newLinks });
    }
    else if (layout === "forceAtlas2") {
      // Reset to letting react-force-graph do default layout by clearing positions
      let resetNodes = graphData.nodes.map(node => {
        const n = { ...node };
        delete n.x;
        delete n.y;
        delete n.vx;
        delete n.vy;
        return n;
      });
      setGraphData({ nodes: resetNodes, links: graphData.links });
    }
  }, [layout, graphData.nodes.length]);

  // Zoom and center graph after layout changes
  useEffect(() => {
    if (fgRef.current && graphData.nodes.length) {
      // Give time for graph to update before zoomToFit
      setTimeout(() => {
        fgRef.current.zoomToFit(400, 100); // 400ms animation, 100px padding
      }, 500);
    }
  }, [graphData]);

  return (
    <div>
      <div style={{ marginBottom: "10px" }}>
        <label>Layout: </label>
        <select value={layout} onChange={e => setLayout(e.target.value)}>
          <option value="forceAtlas2">ForceAtlas2 (default)</option>
          <option value="fruchterman">Fruchterman–Reingold</option>
          <option value="circular">Circular</option>
          <option value="random">Random</option>
        </select>
      </div>
      <div style={{ width: "100vw", height: "100vh" }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel={node => `${node.id} (${node.industry})`}
          nodeAutoColorBy="industry"
          linkDirectionalParticles={2}
          linkDirectionalParticleSpeed={0.005}
          width={window.innerWidth}
          height={window.innerHeight}
        />
      </div>
    </div>
  );
}
