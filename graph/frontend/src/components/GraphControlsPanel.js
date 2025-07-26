import React, { useEffect } from "react";
import {
  Select,
  MenuItem,
  InputLabel,
  FormControl,
} from "@mui/material";
import { useSelector, useDispatch } from "react-redux";
import IndustryColorPicker from "./IndustryColorPicker";
import {
  updateIndustryColor as updateIndustryColorAction,
  setSelectedYear,
  setSelectedFilter,
} from "../store/fileSlice";

export default function GraphControlsPanel({
  fileInputRef,
  openFileDialog,
  handleFileChange,
  fileName,
}) {
  const dispatch = useDispatch();

  const selectedYear = useSelector((state) => state.file.selectedYear);
  const selectedFilter = useSelector((state) => state.file.selectedFilter);
  const industries = useSelector((state) => state.file.industries);
  const industryColors = useSelector((state) => state.file.industryColors);

  const updateIndustryColor = (industry, color) => {
    dispatch(updateIndustryColorAction({ industry, color }));
  };

  const loadYearFile = async (year, filter) => {
    try {
      const formattedFilter = filter.toLowerCase().replace(/\s+/g, "_");
      const response = await fetch(`/data/${year}/graph_${formattedFilter}.json`);

      if (!response.ok) throw new Error(`Failed to load graph for ${year} with filter ${filter}`);

      const json = await response.json();

      if (!json || Object.keys(json).length === 0) {
        alert(`Graph data for ${year} with filter "${filter}" is empty.`);
        handleFileChange({ target: { files: [] } });
        return;
      }

      const file = new File(
        [JSON.stringify(json)],
        `graph_${year}_${formattedFilter}.json`,
        { type: "application/json" }
      );

      const syntheticEvent = {
        target: {
          files: [file],
        },
      };

      handleFileChange(syntheticEvent);
    } catch (error) {
      console.error("Error loading JSON:", { year, filter, error });
      handleFileChange({ target: { files: [] } });
    }
  };

  // Auto-load graph on year or filter change
  useEffect(() => {
    loadYearFile(selectedYear, selectedFilter);
  }, [selectedYear, selectedFilter]);

  const handleYearChange = (event) => {
    dispatch(setSelectedYear(event.target.value));
  };

  const handleFilterChange = (event) => {
    dispatch(setSelectedFilter(event.target.value));
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

      {/* Color Picker */}
      <IndustryColorPicker
        industries={industries}
        industryColors={industryColors}
        updateIndustryColor={updateIndustryColor}
      />
    </div>
  );
}
