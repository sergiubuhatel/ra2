import chroma from "chroma-js";

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