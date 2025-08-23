// src/utils/generateTopologyLinks.js
export function generateTopologyLinks(nodes, originalLinks, topology) {
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
