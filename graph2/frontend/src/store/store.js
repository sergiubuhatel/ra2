import { configureStore } from "@reduxjs/toolkit";
import fileReducer from "./fileSlice"; // adjust path as needed

export const store = configureStore({
  reducer: {
    file: fileReducer,
    // other reducers...
  },
});
