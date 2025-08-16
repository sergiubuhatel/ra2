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

  // Long name → industry number (make sure this matches your real data)
  const industryNameToNumber = {
    "Agriculture": 1,
    "Food Products": 2,
    "Candy & Soda": 3,
    "Beer & Liquor": 4,
    "Tobacco Products": 5,
    "Recreation": 6,
    "Entertainment": 7,
    "Printing and Publishing": 8,
    "Consumer Goods": 9,
    "Apparel": 10,
    "Healthcare": 13,
    "Medical Equipment": 12,
    "Pharmaceutical Products": 14,
    "Chemicals": 15,
    "Rubber and Plastic Products": 16,
    "Textiles": 17,
    "Construction Materials": 18,
    "Construction": 19,
    "Steel Works Etc": 20,
    "Fabricated Products": 21,
    "Machinery": 22,
    "Electrical Equipment": 23,
    "Automobiles and Trucks": 24,
    "Aircraft": 25,
    "Shipbuilding, Railroad Equipment": 26,
    "Defense": 27,
    "Precious Metals": 28,
    "Non-Metallic and Industrial Metal Mining": 29,
    "Coal": 30,
    "Petroleum and Natural Gas": 31,
    "Utilities": 32,
    "Communication": 33,
    "Personal Services": 34,
    "Business Services": 35,
    "Computers": 36,
    "Electronic Equipment": 37,
    "Measuring and Control Equipment": 38,
    "Business Supplies": 39,
    "Shipping Containers": 40,
    "Transportation": 41,
    "Wholesale": 42,
    "Retail": 43,
    "Restaurants, Hotels, Motels": 44,
    "Banking": 45,
    "Insurance": 46,
    "Real Estate": 47,
    "Trading": 48,
    "Almost Nothing": 49,
  };

  const filterOptions = [
    "Top 50", "Top 100", "Top 200",
    ...Object.keys(industryNameToNumber),
  ];

  const loadYearFile = async (year, filter) => {
    try {
      const topOptions = ["Top 50", "Top 100", "Top 200"];
      let fileName;

      if (topOptions.includes(filter)) {
        const formattedFilter = filter.toLowerCase().replace(/\s+/g, "_");
        fileName = `graph_${formattedFilter}.json`;
      } else {
        const industryNumber = industryNameToNumber[filter];
        if (industryNumber === undefined) {
          alert(`Unknown industry selected: ${filter}`);
          handleFileChange({ target: { files: [] } });
          return;
        }
        fileName = `graph_industry_${industryNumber}.json`;
      }

      const response = await fetch(`/data/${year}/${fileName}`);
      if (!response.ok) throw new Error(`Failed to load ${fileName}`);

      const json = await response.json();
      if (!json || Object.keys(json).length === 0) {
        alert(`Graph data for "${filter}" (${fileName}) is empty.`);
        handleFileChange({ target: { files: [] } });
        return;
      }

      const file = new File([JSON.stringify(json)], fileName, {
        type: "application/json",
      });

      handleFileChange({ target: { files: [file] } });
    } catch (error) {
      console.error("Error loading graph data:", { year, filter, error });
      handleFileChange({ target: { files: [] } });
    }
  };

  useEffect(() => {
    loadYearFile(selectedYear, selectedFilter);
  }, [selectedYear, selectedFilter]);

  const handleYearChange = (event) => {
    dispatch(setSelectedYear(event.target.value));
  };

  const handleFilterChange = (event) => {
    dispatch(setSelectedFilter(event.target.value));
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
      {/* Year dropdown */}
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel id="year-select-label">Year</InputLabel>
        <Select
          labelId="year-select-label"
          value={selectedYear}
          label="Year"
          onChange={handleYearChange}
        >
          {[...Array(2023 - 2017 + 1)].map((_, idx) => {
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
