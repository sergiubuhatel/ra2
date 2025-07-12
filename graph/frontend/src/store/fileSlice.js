import { createSlice } from "@reduxjs/toolkit";

const fileSlice = createSlice({
  name: "file",
  initialState: {
    content: null,
    name: "",
  },
  reducers: {
    setFileContent(state, action) {
      state.content = action.payload;
    },
    setFileName(state, action) {
      state.name = action.payload;
    },
  },
});

export const { setFileContent, setFileName } = fileSlice.actions;

export default fileSlice.reducer;
