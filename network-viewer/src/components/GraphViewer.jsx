import React, { useState, useEffect, useRef } from "react";
import ForceGraph2D from "react-force-graph-2d";
import * as d3 from "d3-force";
import { generateTopologyLinks } from "../utils/generateTopologyLinks";
import { industryNameToNumber } from "../utils/industryMapping";

export default function GraphViewer() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [layout, setLayout] = useState("forceAtlas2");
  const [topology, setTopology] = useState("original");
  const [dataset, setDataset] = useState("Top 50"); // Top 50/100/200 or industry
  const [year, setYear] = useState("2017"); // default year
  const fgRef = useRef();

  // Build dataset options: Top N + industries in alphabetical order
  const datasetOptions = [
    "Top 50",
    "Top 100",
    "Top 200",
    ...Object.keys(industryNameToNumber).sort((a, b) => a.localeCompare(b))
  ];

  // Load graph data based on dataset and year
  useEffect(() => {
    let filename = "";

    if (dataset.startsWith("Top")) {
      // Top N dataset
      filename = `/data/${year}/${
        dataset === "Top 50" ? "graph_top_50.json" :
        dataset === "Top 100" ? "graph_top_100.json" :
        "graph_top_200.json"
      }`;
    } else {
      // Industry dataset
      const code = industryNameToNumber[dataset];
      filename = `/data/${year}/graph_industry_${code}.json`;
    }

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
  }, [dataset, year]);

  // Apply topology + layout safely
  useEffect(() => {
    if (!graphData.nodes.length) return;

    const newNodes = graphData.nodes.map(node => ({ ...node }));

    // Find node with highest eigenvector centrality
    const maxECNode = newNodes.reduce((maxNode, node) =>
      (node.eigenvector_centrality || 0) > (maxNode.eigenvector_centrality || 0) ? node : maxNode
    , newNodes[0]);

    // Swap max EC node to index 0 if using hub-spoke/star
    if (topology === "hub-spoke" || topology === "star") {
      const index = newNodes.findIndex(n => n.id === maxECNode.id);
      if (index > 0) [newNodes[0], newNodes[index]] = [newNodes[index], newNodes[0]];
    }

    const newLinks = generateTopologyLinks(newNodes, graphData.links, topology);

    const nodeById = new Map(newNodes.map(n => [n.id, n]));
    const safeLinks = newLinks
      .map(link => ({
        ...link,
        source: nodeById.get(link.source),
        target: nodeById.get(link.target)
      }))
      .filter(link => link.source && link.target);

    // Layout positioning
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

      // Fix the highest EC node at the center
      maxECNode.fx = 0;
      maxECNode.fy = 0;

      sim.stop();
      for (let i = 0; i < 300; i++) sim.tick();

      // Optionally release it after simulation
      delete maxECNode.fx;
      delete maxECNode.fy;
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
        <label style={{ marginRight: 10 }}>Year:</label>
        <select value={year} onChange={e => setYear(e.target.value)}>
          {["2017","2018","2019","2020","2021","2022","2023"].map(y => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>

        <label style={{ marginLeft: 20, marginRight: 10 }}>Dataset:</label>
        <select value={dataset} onChange={e => setDataset(e.target.value)}>
          {datasetOptions.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
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
