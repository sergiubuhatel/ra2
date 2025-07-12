import React from "react";
import { useSelector, useDispatch } from "react-redux";
import Button from "@mui/material/Button";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import IndustryColorPicker from "./IndustryColorPicker";
import { updateIndustryColor as updateIndustryColorAction } from "../store/fileSlice"; // adjust path as needed

export default function GraphControlsPanel({
  fileInputRef,
  openFileDialog,
  handleFileChange,
  fileName,
}) {
  const dispatch = useDispatch();
  const industries = useSelector((state) => state.file.industries);
  const industryColors = useSelector((state) => state.file.industryColors);

  const updateIndustryColor = (industry, color) => {
    dispatch(updateIndustryColorAction({ industry, color }));
  };

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

      <IndustryColorPicker
        industries={industries}
        industryColors={industryColors}
        updateIndustryColor={updateIndustryColor}
      />
    </div>
  );
}
