import React, { useState, useEffect, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import * as d3 from "d3-force";

// Generate links based on selected topology
function generateTopologyLinks(nodes, originalLinks, topology) {
  const n = nodes.length;
  if (topology === "hub-spoke" || topology === "star") {
    const hub = nodes[0].id;
    return nodes.slice(1).map(node => ({
      source: hub,
      target: node.id,
      value: 1
    }));
  } else if (topology === "mesh") {
    let links = [];
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        links.push({ source: nodes[i].id, target: nodes[j].id, value: 1 });
      }
    }
    return links;
  } else if (topology === "point-to-point") {
    let links = [];
    for (let i = 0; i < n - 1; i++) {
      links.push({ source: nodes[i].id, target: nodes[i + 1].id, value: 1 });
    }
    return links;
  } else {
    // original topology
    return originalLinks;
  }
}

export default function GraphViewer() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [layout, setLayout] = useState("forceAtlas2");
  const [topology, setTopology] = useState("original");
  const fgRef = useRef();

  // Load graph data once
  useEffect(() => {
    fetch("/graph_top_50.json")
      .then(res => res.json())
      .then(data => {
        const originalLinks = data.edges.map(e => ({
          source: e.source,
          target: e.target,
          value: e.weight
        }));
        setGraphData({ nodes: data.nodes, links: originalLinks });
      });
  }, []);

  // Apply topology and layout when either changes or data loaded
  useEffect(() => {
    if (!graphData.nodes.length) return;

    // Clone nodes to avoid mutating state
    let newNodes = graphData.nodes.map(node => ({ ...node }));

    // Generate links based on selected topology
    const newLinks = generateTopologyLinks(newNodes, graphData.links, topology);

    // Map node ids to node objects (needed when nodes have fixed positions)
    const nodeById = new Map(newNodes.map(n => [n.id, n]));

    // Prepare links with node objects for ForceGraph2D (except for forceAtlas2)
    const linksWithNodeObjects = newLinks.map(link => ({
      ...link,
      source: nodeById.get(link.source),
      target: nodeById.get(link.target)
    }));

    if (layout === "random") {
      newNodes.forEach(node => {
        node.x = Math.random() * 800;
        node.y = Math.random() * 600;
        delete node.vx;
        delete node.vy;
      });
      setGraphData({ nodes: newNodes, links: linksWithNodeObjects });
    } else if (layout === "circular") {
      const radius = 300;
      newNodes.forEach((node, i) => {
        const angle = (i / newNodes.length) * 2 * Math.PI;
        node.x = radius * Math.cos(angle);
        node.y = radius * Math.sin(angle);
        delete node.vx;
        delete node.vy;
      });
      setGraphData({ nodes: newNodes, links: linksWithNodeObjects });
    } else if (layout === "fruchterman") {
      // For simulation, links must have source/target as node ids (strings)
      const sim = d3.forceSimulation(newNodes)
        .force("link", d3.forceLink(newLinks).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-150))
        .force("center", d3.forceCenter(0, 0));

      sim.stop();
      for (let i = 0; i < 300; i++) sim.tick();

      setGraphData({ nodes: newNodes, links: linksWithNodeObjects });
    } else if (layout === "forceAtlas2") {
      // Clear positions and velocities so react-force-graph does default layout
      const resetNodes = newNodes.map(node => {
        const n = { ...node };
        delete n.x;
        delete n.y;
        delete n.vx;
        delete n.vy;
        return n;
      });
      setGraphData({ nodes: resetNodes, links: newLinks });
    }
  }, [layout, topology, graphData.nodes.length]);

  // Zoom and center graph after graphData updates
  useEffect(() => {
    if (fgRef.current && graphData.nodes.length) {
      setTimeout(() => {
        fgRef.current.zoomToFit(400, 100);
      }, 500);
    }
  }, [graphData]);

  return (
    <div>
      <div style={{ marginBottom: 10 }}>
        <label style={{ marginRight: 10 }}>Layout:</label>
        <select value={layout} onChange={e => setLayout(e.target.value)}>
          <option value="forceAtlas2">ForceAtlas2 (default)</option>
          <option value="fruchterman">Fruchterman–Reingold</option>
          <option value="circular">Circular</option>
          <option value="random">Random</option>
        </select>

        <label style={{ marginLeft: 20, marginRight: 10 }}>Topology:</label>
        <select value={topology} onChange={e => setTopology(e.target.value)}>
          <option value="original">Original</option>
          <option value="hub-spoke">Hub & Spoke</option>
          <option value="star">Star</option>
          <option value="mesh">Mesh</option>
          <option value="point-to-point">Point-to-Point</option>
        </select>
      </div>

      <div style={{ width: "100vw", height: "100vh" }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={graphData}
          nodeLabel={node => `${node.id} (${node.industry || "N/A"})`}
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
