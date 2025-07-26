import { createSlice } from "@reduxjs/toolkit";

const fileSlice = createSlice({
  name: "file",
  initialState: {
    nodes: [],
    edges: [],
    content: null,
    name: "",
    industries: [],
    industryColors: {},
    selectedYear: 2017,         // <-- new
    selectedFilter: "Top 50",   // <-- new
  },
  reducers: {
    setFileContent(state, action) {
      const content = action.payload || {};
      state.content = content;
      state.nodes = content.nodes || [];
      state.edges = content.edges || [];
    },
    setFileName(state, action) {
      state.name = action.payload;
    },
    setIndustries(state, action) {
      state.industries = action.payload;
    },
    setIndustryColors(state, action) {
      state.industryColors = action.payload;
    },
    updateIndustryColor(state, action) {
      const { industry, color } = action.payload;
      state.industryColors[industry] = color;
    },
    removeNode(state, action) {
      const nodeId = action.payload;
      state.nodes = state.nodes.filter((node) => node.id !== nodeId);
      state.edges = state.edges.filter(
        (edge) => edge.source !== nodeId && edge.target !== nodeId
      );
    },

    // ✅ new reducers
    setSelectedYear(state, action) {
      state.selectedYear = action.payload;
    },
    setSelectedFilter(state, action) {
      state.selectedFilter = action.payload;
    },
  },
});

export const {
  setFileContent,
  setFileName,
  setIndustries,
  setIndustryColors,
  updateIndustryColor,
  removeNode,
  setSelectedYear,       // <-- export new actions
  setSelectedFilter,     // <-- export new actions
} = fileSlice.actions;

export default fileSlice.reducer;
