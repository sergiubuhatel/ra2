import React, { useState } from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import {
  faEye,
  faEyeSlash,
  faPalette,
} from "@fortawesome/free-solid-svg-icons";

// Simple color input component
function ColorPicker({ color, onChange }) {
  return (
    <input
      type="color"
      value={color}
      onChange={(e) => onChange(e.target.value)}
      style={{ width: 40, height: 30, border: "none", cursor: "pointer" }}
    />
  );
}

export default function IndustryColorPicker({
  industries,
  industryColors,
  updateIndustryColor,
}) {
  const [showColors, setShowColors] = useState(false);

  if (!industries.length) return null;

  return (
    <>
      <div
        onClick={() => setShowColors((prev) => !prev)}
        title={showColors ? "Hide industry colors" : "Show industry colors"}
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          backgroundColor: "#f4f4f4",
          border: "1px solid #ccc",
          borderRadius: 4,
          padding: "6px 10px",
          marginBottom: 8,
          cursor: "pointer",
          fontWeight: "bold",
          boxShadow: "1px 1px 3px rgba(0,0,0,0.1)",
          userSelect: "none",
        }}
      >
        <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <FontAwesomeIcon icon={faPalette} />
          Industry Colors
        </span>
        <FontAwesomeIcon icon={showColors ? faEyeSlash : faEye} />
      </div>

      {showColors &&
        industries.map((industry) => (
          <div
            key={industry}
            style={{
              display: "flex",
              alignItems: "center",
              marginBottom: 8,
              gap: 8,
              flexWrap: "nowrap",
            }}
          >
            <div
              style={{
                flex: "1 1 auto",
                whiteSpace: "nowrap",
                overflow: "hidden",
                textOverflow: "ellipsis",
              }}
              title={industry}
            >
              {industry}
            </div>
            <ColorPicker
              color={industryColors[industry] || "#888888"}
              onChange={(color) => updateIndustryColor(industry, color)}
            />
          </div>
        ))}
    </>
  );
}
