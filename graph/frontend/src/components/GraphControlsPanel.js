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
  const [selectedYear, setSelectedYear] = useState(2017); // default year
  const [selectedFilter, setSelectedFilter] = useState("Top 50"); // default filter

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

      if (!json || Object.keys(json).length === 0) {
        alert(`Graph data for ${year} is empty.`);
        handleFileChange({ target: { files: [] } });
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
      handleFileChange({ target: { files: [] } });
    }
  };

  const handleYearChange = (event) => {
    const year = event.target.value;
    setSelectedYear(year);
    // No auto-loading here
  };

  const handleFilterChange = (event) => {
    setSelectedFilter(event.target.value);
  };

  const handleViewGraph = () => {
    loadYearFile(selectedYear);
    // You may also want to use selectedFilter to adjust logic in the future
  };

  const filterOptions = [
    "Top 50", "Top 100", "Top 200", "Agriculture", "Aircraft", "Autos", "Banks", "Beer",
    "BldMt", "Books", "Business Services", "Chemicals", "Chips", "Clothes", "Construction",
    "Coal", "Computers", "Drugs", "Electronic Equipments", "Fabricated Products", "Finance",
    "Food", "Fun", "Gold", "Guns", "Healthcare", "Household", "Insurance", "Lab Equipments",
    "Mach", "Meals", "Medical Equipment", "Mines", "Oil", "Paper", "PerSv", "Real Estate",
    "Retail", "Rubber", "Ships", "Smokem", "Soda", "Steel", "Telecom", "Textiles", "Toys",
    "Transportation", "Utilities", "Wholesale", "Other"
  ];

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

      {/* Filter dropdown */}
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="filter-select-label">Filter</InputLabel>
        <Select
          labelId="filter-select-label"
          value={selectedFilter}
          label="Filter"
          onChange={handleFilterChange}
        >
          {filterOptions.map((option) => (
            <MenuItem key={option} value={option}>
              {option}
            </MenuItem>
          ))}
        </Select>
      </FormControl>

      {/* View Graph button */}
      <Button
        variant="contained"
        color="primary"
        fullWidth
        sx={{ mb: 2 }}
        onClick={handleViewGraph}
      >
        View Graph
      </Button>

      <IndustryColorPicker
        industries={industries}
        industryColors={industryColors}
        updateIndustryColor={updateIndustryColor}
      />
    </div>
  );
}
