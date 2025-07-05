import React from "react";
import Button from "@mui/material/Button";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import IndustryColorPicker from "./IndustryColorPicker"; // 👈 Import the new component

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
        <div
          style={{
            marginBottom: 20,
            fontSize: "0.9rem",
            color: "#555",
          }}
        >
          {fileName}
        </div>
      )}

      {/* Extracted component */}
      <IndustryColorPicker
        industries={industries}
        industryColors={industryColors}
        updateIndustryColor={updateIndustryColor}
      />
    </div>
  );
}
