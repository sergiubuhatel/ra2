import React, { useState, useEffect } from "react";
import {
  Button,
  Select,
  MenuItem,
  InputLabel,
  FormControl,
} from "@mui/material";
import { useSelector, useDispatch } from "react-redux";
import UploadFileIcon from "@mui/icons-material/UploadFile";
import IndustryColorPicker from "./IndustryColorPicker";
import { updateIndustryColor as updateIndustryColorAction } from "../store/fileSlice";

export default function GraphControlsPanel({
  fileInputRef,
  openFileDialog,
  handleFileChange,
  fileName,
}) {
  const [selectedYear, setSelectedYear] = useState(2017); // default year 2017

  const dispatch = useDispatch();
  const industries = useSelector((state) => state.file.industries);
  const industryColors = useSelector((state) => state.file.industryColors);

  const updateIndustryColor = (industry, color) => {
    dispatch(updateIndustryColorAction({ industry, color }));
  };

  const loadYearFile = async (year) => {
    try {
      const response = await fetch(`/data/${year}/graph_with_centrality.json`);
      if (!response.ok) throw new Error(`Failed to load graph for ${year}`);

      const json = await response.json();

      // Check if JSON is empty or invalid in some way
      if (!json || Object.keys(json).length === 0) {
        alert(`Graph data for ${year} is empty.`);
        handleFileChange({ target: { files: [] } }); // clear graph
        return;
      }

      const file = new File(
        [JSON.stringify(json)],
        `graph_${year}.json`,
        { type: "application/json" }
      );

      const syntheticEvent = {
        target: {
          files: [file],
        },
      };

      handleFileChange(syntheticEvent);
    } catch (error) {
      console.error("Error loading JSON for year:", year, error);

      // Clear the graph on error
      handleFileChange({ target: { files: [] } });
    }
  };

  const handleYearChange = (event) => {
    const year = event.target.value;
    setSelectedYear(year);
    loadYearFile(year);
  };

  // Load 2017 on mount
  useEffect(() => {
    loadYearFile(2017);
  }, []);

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
      {/* Year dropdown */}
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="year-select-label">Year</InputLabel>
        <Select
          labelId="year-select-label"
          value={selectedYear}
          label="Year"
          onChange={handleYearChange}
        >
          {[...Array(2025 - 2017 + 1)].map((_, idx) => {
            const year = 2017 + idx;
            return (
              <MenuItem key={year} value={year}>
                {year}
              </MenuItem>
            );
          })}
        </Select>
      </FormControl>

      <IndustryColorPicker
        industries={industries}
        industryColors={industryColors}
        updateIndustryColor={updateIndustryColor}
      />
    </div>
  );
}
