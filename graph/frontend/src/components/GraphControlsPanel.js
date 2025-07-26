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

  // Map from long industry name to short code
  const industryNameToCode = {
    "Agriculture": "Agric",
    "Food Products": "Food",
    "Candy & Soda": "Soda",
    "Beer & Liquor": "Beer",
    "Tobacco Products": "Smoke",
    "Recreation": "Toys",
    "Entertainment": "Fun",
    "Printing and Publishing": "Books",
    "Consumer Goods": "Hshld",
    "Apparel": "Clths",
    "Healthcare": "Hlth",
    "Medical Equipment": "MedEq",
    "Pharmaceutical Products": "Drugs",
    "Chemicals": "Chems",
    "Rubber and Plastic Products": "Rubbr",
    "Textiles": "Txtls",
    "Construction Materials": "BldMt",
    "Construction": "Cnstr",
    "Steel Works Etc": "Steel",
    "Fabricated Products": "FabPr",
    "Machinery": "Mach",
    "Electrical Equipment": "ElcEq",
    "Automobiles and Trucks": "Autos",
    "Aircraft": "Aero",
    "Shipbuilding, Railroad Equipment": "Ships",
    "Defense": "Guns",
    "Precious Metals": "Gold",
    "Non-Metallic and Industrial Metal Mining": "Mines",
    "Coal": "Coal",
    "Petroleum and Natural Gas": "Oil",
    "Utilities": "Util",
    "Communication": "Telcm",
    "Personal Services": "PerSv",
    "Business Services": "BusSv",
    "Computers": "Comps",
    "Electronic Equipment": "Chips",
    "Measuring and Control Equipment": "LabEq",
    "Business Supplies": "Paper",
    "Shipping Containers": "Boxes",
    "Transportation": "Trans",
    "Wholesale": "Whlsl",
    "Retail": "Rtail",
    "Restaurants, Hotels, Motels": "Meals",
    "Banking": "Banks",
    "Insurance": "Insur",
    "Real Estate": "RlEst",
    "Trading": "Fin",
    "Almost Nothing": "Other",
  };

  const filterOptions = [
    "Top 50", "Top 100", "Top 200",
    "Agriculture",
    "Food Products",
    "Candy & Soda",
    "Beer & Liquor",
    "Tobacco Products",
    "Recreation",
    "Entertainment",
    "Printing and Publishing",
    "Consumer Goods",
    "Apparel",
    "Healthcare",
    "Medical Equipment",
    "Pharmaceutical Products",
    "Chemicals",
    "Rubber and Plastic Products",
    "Textiles",
    "Construction Materials",
    "Construction",
    "Steel Works Etc",
    "Fabricated Products",
    "Machinery",
    "Electrical Equipment",
    "Automobiles and Trucks",
    "Aircraft",
    "Shipbuilding, Railroad Equipment",
    "Defense",
    "Precious Metals",
    "Non-Metallic and Industrial Metal Mining",
    "Coal",
    "Petroleum and Natural Gas",
    "Utilities",
    "Communication",
    "Personal Services",
    "Business Services",
    "Computers",
    "Electronic Equipment",
    "Measuring and Control Equipment",
    "Business Supplies",
    "Shipping Containers",
    "Transportation",
    "Wholesale",
    "Retail",
    "Restaurants, Hotels, Motels",
    "Banking",
    "Insurance",
    "Real Estate",
    "Trading",
    "Almost Nothing",
  ];

  const loadYearFile = async (year, filter) => {
    try {
      const topOptions = ["Top 50", "Top 100", "Top 200"];
      // If filter is an industry, load Top 200 and filter nodes client-side
      const effectiveFilter = topOptions.includes(filter) ? filter : "Top 200";
      const formattedFilter = effectiveFilter.toLowerCase().replace(/\s+/g, "_");

      const response = await fetch(`/data/${year}/graph_${formattedFilter}.json`);
      if (!response.ok) throw new Error(`Failed to load graph for ${year} with filter ${filter}`);
      const json = await response.json();

      if (!json || Object.keys(json).length === 0) {
        alert(`Graph data for ${year} with filter "${filter}" is empty.`);
        handleFileChange({ target: { files: [] } });
        return;
      }

      let filteredJson = json;

      if (!topOptions.includes(filter)) {
        // Convert long industry name to short code
        const industryCode = industryNameToCode[filter];
        if (!industryCode) {
          alert(`Unknown industry selected: ${filter}`);
          handleFileChange({ target: { files: [] } });
          return;
        }

        // Filter nodes by industry short code
        const filteredNodes = json.nodes.filter((node) => node.industry === industryCode);
        const nodeIds = new Set(filteredNodes.map((n) => n.id));

        // Filter edges to only those connecting filtered nodes
        const filteredEdges = json.edges.filter(
          (edge) => nodeIds.has(edge.source) && nodeIds.has(edge.target)
        );

        filteredJson = { nodes: filteredNodes, edges: filteredEdges };
      }

      const file = new File(
        [JSON.stringify(filteredJson)],
        `graph_${year}_${filter.replace(/\s+/g, "_")}.json`,
        { type: "application/json" }
      );

      handleFileChange({ target: { files: [file] } });
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
