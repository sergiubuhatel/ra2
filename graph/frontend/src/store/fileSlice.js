import { createSlice } from "@reduxjs/toolkit";

const fileSlice = createSlice({
  name: "file",
  initialState: {
    content: null,
    name: "",
    industries: [],             // ← NEW
    industryColors: {},         // ← NEW
  },
  reducers: {
    setFileContent(state, action) {
      state.content = action.payload;
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
  },
});

export const {
  setFileContent,
  setFileName,
  setIndustries,
  setIndustryColors,
  updateIndustryColor,
} = fileSlice.actions;

export default fileSlice.reducer;
