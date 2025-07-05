import React from "react";
import Button from "@mui/material/Button";
import UploadFileIcon from "@mui/icons-material/UploadFile";

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

export default function GraphControlsPanel({
  fileInputRef,
  openFileDialog,
  handleFileChange,
  fileName,
  industries,
  industryColors,
  updateIndustryColor,
  nodeSizeFactor,
  setNodeSizeFactor,
  edgeThickness,
  setEdgeThickness,
}) {
  return (
    <div
      style={{
        width: 220,
        borderRight: "1px solid #ccc",
        padding: 12,
        boxSizing: "border-box",
        overflowY: "auto",
        background: "#CECECC",
      }}
    >
      <Button
        variant="contained"
        color="primary"
        fullWidth
        startIcon={<UploadFileIcon />}
        onClick={openFileDialog}
        sx={{ mb: 2 }}
      >
        Load Graph JSON
      </Button>

      <input
        ref={fileInputRef}
        type="file"
        accept=".json"
        onChange={handleFileChange}
        style={{ display: "none" }}
      />

      {fileName && (
        <div style={{ marginBottom: 20, fontSize: "0.9rem", color: "#555" }}>{fileName}</div>
      )}

      {industries.length > 0 && (
        <>
          <div style={{ marginBottom: 8, fontWeight: "bold" }}>Industry Colors</div>
          {industries.map((industry) => (
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
      )}

      <div style={{ marginTop: 20 }}>
        <div style={{ fontWeight: "bold", marginBottom: 8 }}>Node Size</div>
        <input
          type="range"
          min="20"
          max="100"
          step="1"
          value={nodeSizeFactor}
          onChange={(e) => setNodeSizeFactor(Number(e.target.value))}
          style={{ width: "100%" }}
        />
        <div style={{ textAlign: "center", marginTop: 8 }}>
          Size Factor: {nodeSizeFactor}
        </div>
      </div>

      <div style={{ marginTop: 20 }}>
        <div style={{ fontWeight: "bold", marginBottom: 8 }}>Edge Thickness Threshold</div>
        <input
          type="range"
          min="1"
          max="25"
          step="0.1"
          value={edgeThickness}
          onChange={(e) => setEdgeThickness(Number(e.target.value))}
          style={{ width: "100%" }}
        />
        <div style={{ textAlign: "center", marginTop: 8 }}>
          Thickness: {edgeThickness}
        </div>
      </div>
    </div>
  );
}
