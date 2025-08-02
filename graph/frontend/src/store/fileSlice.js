import { createSlice } from "@reduxjs/toolkit";

const fileSlice = createSlice({
  name: "file",
  initialState: {
    content: null,
    name: "",
    industries: [],
    industryColors: {},
    selectedYear: 2017,
    selectedFilter: "Top 50",
  },
  reducers: {
    setFileContent(state, action) {
      const content = action.payload || {};
      state.content = content;
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
      if (state.content) {
        state.content.nodes = (state.content.nodes || []).filter(
          (node) => node.id !== nodeId
        );
        state.content.edges = (state.content.edges || []).filter(
          (edge) => edge.source !== nodeId && edge.target !== nodeId
        );
      }
    },
    // <-- New action to add a node and edges
    addNodeWithEdges(state, action) {
      const { node, edges } = action.payload;

      if (!state.content) {
        state.content = {
          nodes: [],
          edges: [],
        };
      }

      // Add the new node
      state.content.nodes = state.content.nodes || [];
      state.content.nodes.push(node);

      // Add the new edges
      state.content.edges = state.content.edges || [];
      state.content.edges.push(...edges);
    },
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
  addNodeWithEdges,  // <-- export the new action
  setSelectedYear,
  setSelectedFilter,
} = fileSlice.actions;

export default fileSlice.reducer;
