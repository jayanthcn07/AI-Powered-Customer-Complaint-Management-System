import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import * as apiClient from "../api/client";

export const fetchComplaints = createAsyncThunk(
  "complaints/fetchAll",
  async (params = {}) => apiClient.listComplaints(params)
);

export const fetchComplaint = createAsyncThunk(
  "complaints/fetchOne",
  async (id) => apiClient.getComplaint(id)
);

export const fetchStats = createAsyncThunk(
  "complaints/fetchStats",
  async () => apiClient.getStats()
);

export const createComplaintThunk = createAsyncThunk(
  "complaints/create",
  async (payload) => apiClient.createComplaint(payload)
);

export const updateComplaintThunk = createAsyncThunk(
  "complaints/update",
  async ({ id, payload }) => apiClient.updateComplaint(id, payload)
);

export const deleteComplaintThunk = createAsyncThunk(
  "complaints/delete",
  async (id) => {
    await apiClient.deleteComplaint(id);
    return id;
  }
);

export const reanalyzeComplaintThunk = createAsyncThunk(
  "complaints/reanalyze",
  async (id) => apiClient.reanalyzeComplaint(id)
);

const complaintsSlice = createSlice({
  name: "complaints",
  initialState: {
    items: [],
    selected: null,
    stats: null,
    status: "idle", // idle | loading | succeeded | failed
    error: null,
    filters: { status: "", severity: "", risk_level: "", search: "" },
  },
  reducers: {
    setFilters(state, action) {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearSelected(state) {
      state.selected = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchComplaints.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchComplaints.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.items = action.payload;
      })
      .addCase(fetchComplaints.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.error.message;
      })
      .addCase(fetchComplaint.fulfilled, (state, action) => {
        state.selected = action.payload;
      })
      .addCase(fetchStats.fulfilled, (state, action) => {
        state.stats = action.payload;
      })
      .addCase(createComplaintThunk.fulfilled, (state, action) => {
        state.items.unshift(action.payload);
      })
      .addCase(updateComplaintThunk.fulfilled, (state, action) => {
        const idx = state.items.findIndex((c) => c.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
        if (state.selected?.id === action.payload.id) state.selected = action.payload;
      })
      .addCase(reanalyzeComplaintThunk.fulfilled, (state, action) => {
        const idx = state.items.findIndex((c) => c.id === action.payload.id);
        if (idx !== -1) state.items[idx] = action.payload;
        if (state.selected?.id === action.payload.id) state.selected = action.payload;
      })
      .addCase(deleteComplaintThunk.fulfilled, (state, action) => {
        state.items = state.items.filter((c) => c.id !== action.payload);
      });
  },
});

export const { setFilters, clearSelected } = complaintsSlice.actions;
export default complaintsSlice.reducer;
