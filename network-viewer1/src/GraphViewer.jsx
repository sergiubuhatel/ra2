import React, { useState, useEffect } from "react";
import ForceGraph2D from "react-force-graph-2d";
import * as d3 from "d3-force";

export default function GraphViewer() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [layout, setLayout] = useState("forceAtlas2");

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

  const applyLayout = () => {
    if (layout === "random") {
      graphData.nodes.forEach(node => {
        node.x = Math.random() * 800;
        node.y = Math.random() * 600;
      });
    }
    else if (layout === "circular") {
      const radius = 300;
      graphData.nodes.forEach((node, i) => {
        const angle = (i / graphData.nodes.length) * 2 * Math.PI;
        node.x = radius * Math.cos(angle);
        node.y = radius * Math.sin(angle);
      });
    }
    else if (layout === "fruchterman") {
      const sim = d3.forceSimulation(graphData.nodes)
        .force("link", d3.forceLink(graphData.links).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-150))
        .force("center", d3.forceCenter(0, 0))
        .stop();
      for (let i = 0; i < 300; i++) sim.tick();
    }
    // ForceAtlas2 is the default, no extra step
  };

  return (
    <div>
      <div style={{ marginBottom: "10px" }}>
        <label>Layout: </label>
        <select value={layout} onChange={e => setLayout(e.target.value)}>
          <option value="forceAtlas2">ForceAtlas2</option>
          <option value="fruchterman">Fruchterman–Reingold</option>
          <option value="circular">Circular</option>
          <option value="random">Random</option>
        </select>
      </div>
      <ForceGraph2D
        graphData={graphData}
        nodeLabel={node => `${node.id} (${node.industry})`}
        nodeAutoColorBy="industry"
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        onEngineStop={applyLayout}
        width={800}
        height={600}
      />
    </div>
  );
}
