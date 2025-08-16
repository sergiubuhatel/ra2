const colorPalette = [
  "#e41a1c", // red
  "#377eb8", // blue
  "#4daf4a", // green
  "#984ea3", // purple
  "#ff7f00", // orange
  "#ffff33", // yellow
  "#a65628", // brown
  "#f781bf", // pink
  "#999999", // gray
  "#66c2a5", // aqua
  "#fc8d62", // coral
  "#8da0cb", // periwinkle
  "#e78ac3", // magenta
  "#a6d854", // lime
  "#ffd92f", // bright yellow
  "#e5c494", // beige
  "#b3b3b3", // silver
];

function hashStringToInt(str) {
  str = String(str || "");
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash * 31 + str.charCodeAt(i)) >>> 0;
  }
  return hash;
}

export function getDeterministicColor(key) {
  const hash = hashStringToInt(key);
  const index = hash % colorPalette.length;
  return colorPalette[index];
}

export function getRandomColor() {
    return "#" + Math.floor(Math.random() * 0xffffff).toString(16).padStart(6, "0");
}

// utils/hexToRgba.js
export function hexToRgba(hex, alpha = 1) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r}, ${g}, ${b}, ${alpha.toFixed(2)})`;
}

export function blendWithBlack(hex, amount) {
  // hex: "#RRGGBB", amount: 0 (no blend) to 1 (full black)
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);

  const blend = (channel) =>
    Math.round(channel * (1 - amount)); // blend toward 0 (black)

  return `rgb(${blend(r)}, ${blend(g)}, ${blend(b)})`;
}
