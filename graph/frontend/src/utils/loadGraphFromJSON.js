// src/utils/loadGraphFromJSON.js
import Graph from "graphology";

function industryColor(industry) {
  // Simple color mapping by industry
  const colors = {
    "13": "#ff6f61",
    "34": "#6b5b95",
    "36": "#88b04b",
    "42": "#f7cac9",
    "44": "#92a8d1",
    "3": "#955251",
    "21": "#b565a7",
    "23": "#009b77",
    "24": "#dd4124",
    "30": "#45b8ac",
    "32": "#eFC050",
    "35": "#5b5ea6",
    "47": "#9b2335",
    "-1": "#999999", // unknown
  };
  return colors[industry] || "#999999";
}

export async function loadGraphFromJSON() {
  const response = await fetch("/graph_top50.json");
  const data = await response.json();

  const graph = new Graph();

  data.nodes.forEach(({ id, label, industry }) => {
    graph.addNode(id, {
      label,
      industry,
      size: 6,
      color: industryColor(industry.toString()),
      // Assign random coordinates since Sigma requires numeric x, y
      x: Math.random(),
      y: Math.random(),
      labelColor: "#ffffff"
    });
  });

  data.links.forEach(({ source, target, weight }) => {
    if (graph.hasNode(source) && graph.hasNode(target)) {
      graph.addEdge(source, target, { weight });
    }
  });

  return graph;
}
