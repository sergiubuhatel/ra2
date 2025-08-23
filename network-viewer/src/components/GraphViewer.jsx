import React, { useState, useEffect, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import * as d3 from "d3-force";
import { generateTopologyLinks } from "../utils/generateTopologyLinks";

export default function GraphViewer() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [layout, setLayout] = useState("forceAtlas2");
  const [topology, setTopology] = useState("original");
  const [dataset, setDataset] = useState("Top 50"); // new state for dataset
  const fgRef = useRef();

  // Load graph data based on selected dataset
  useEffect(() => {
    const filename = {
      "Top 50": "/graph_top_50.json",
      "Top 100": "/graph_top_100.json",
      "Top 200": "/graph_top_200.json"
    }[dataset];

    fetch(filename)
      .then(res => res.json())
      .then(data => {
        const originalLinks = data.edges.map(e => ({
          source: e.source,
          target: e.target,
          value: e.weight
        }));
        setGraphData({ nodes: data.nodes, links: originalLinks });
      });
  }, [dataset]);

  // Apply topology + layout safely
  useEffect(() => {
    if (!graphData.nodes.length) return;

    const newNodes = graphData.nodes.map(node => ({ ...node }));
    const newLinks = generateTopologyLinks(newNodes, graphData.links, topology);

    // Filter out links with missing nodes
    const nodeById = new Map(newNodes.map(n => [n.id, n]));
    const safeLinks = newLinks
      .map(link => ({
        ...link,
        source: nodeById.get(link.source),
        target: nodeById.get(link.target)
      }))
      .filter(link => link.source && link.target);

    // Apply layouts
    if (layout === "random") {
      newNodes.forEach(node => {
        node.x = Math.random() * 800;
        node.y = Math.random() * 600;
        delete node.vx;
        delete node.vy;
      });
    } else if (layout === "circular") {
      const radius = 300;
      newNodes.forEach((node, i) => {
        const angle = (i / newNodes.length) * 2 * Math.PI;
        node.x = radius * Math.cos(angle);
        node.y = radius * Math.sin(angle);
        delete node.vx;
        delete node.vy;
      });
    } else if (layout === "fruchterman") {
      const sim = d3.forceSimulation(newNodes)
        .force("link", d3.forceLink(safeLinks).id(d => d.id).distance(100))
        .force("charge", d3.forceManyBody().strength(-150))
        .force("center", d3.forceCenter(0, 0));

      sim.stop();
      for (let i = 0; i < 300; i++) sim.tick();
    }

    setGraphData({ nodes: newNodes, links: safeLinks });
  }, [layout, topology, graphData.nodes.length]);

  // Zoom & center
  useEffect(() => {
    if (fgRef.current && graphData.nodes.length) {
      setTimeout(() => fgRef.current.zoomToFit(400, 100), 500);
    }
  }, [graphData]);

  return (
    <div>
      <div style={{ marginBottom: 10 }}>
        <label style={{ marginRight: 10 }}>Dataset:</label>
        <select value={dataset} onChange={e => setDataset(e.target.value)}>
          <option value="Top 50">Top 50</option>
          <option value="Top 100">Top 100</option>
          <option value="Top 200">Top 200</option>
        </select>

        <label style={{ marginLeft: 20, marginRight: 10 }}>Layout:</label>
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
          nodeLabel={node =>
            `${node.id} (${node.industry || "N/A"}), EC: ${node.eigenvector_centrality?.toFixed(3) || 0}`
          }
          nodeAutoColorBy="industry"
          width={window.innerWidth}
          height={window.innerHeight}
          nodeCanvasObject={(node, ctx, globalScale) => {
            const radius = 1 + (node.eigenvector_centrality || 0) * 20;
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color || "gray";
            ctx.fill();

            ctx.font = `${12 / globalScale}px Sans-Serif`;
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            ctx.fillStyle = "white";
            ctx.fillText(node.id, node.x, node.y);
          }}
        />
      </div>
    </div>
  );
}
