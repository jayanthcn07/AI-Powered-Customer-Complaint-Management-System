import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import * as apiClient from "../api/client";

export const runAnalyzeText = createAsyncThunk(
  "ai/analyzeText",
  async (text) => apiClient.analyzeText(text)
);

export const runAnalyzeUpload = createAsyncThunk(
  "ai/analyzeUpload",
  async (file) => apiClient.analyzeUpload(file)
);

export const runAnalyzeAndLog = createAsyncThunk(
  "ai/analyzeAndLog",
  async (text) => apiClient.analyzeAndLog(text)
);

const aiSlice = createSlice({
  name: "ai",
  initialState: {
    result: null,
    status: "idle", // idle | loading | succeeded | failed
    error: null,
    loggedComplaint: null,
  },
  reducers: {
    clearAiResult(state) {
      state.result = null;
      state.status = "idle";
      state.error = null;
      state.loggedComplaint = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Successful responses
      .addCase(runAnalyzeText.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.result = action.payload;
      })

      .addCase(runAnalyzeUpload.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.result = action.payload;
      })

      .addCase(runAnalyzeAndLog.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.loggedComplaint = action.payload;
        state.result = {
          extracted_fields: action.payload.ai_extracted_fields,
          summary: action.payload.ai_summary,
          completeness_score: action.payload.ai_completeness_score,
          missing_fields: action.payload.ai_missing_fields,
          risk_level: action.payload.ai_risk_level,
          risk_score: action.payload.ai_risk_score,
          risk_rationale: action.payload.ai_risk_rationale,
          root_cause_suggestion:
            action.payload.ai_root_cause_suggestion,
          capa_recommendation:
            action.payload.ai_capa_recommendation,
          is_duplicate: action.payload.ai_is_duplicate,
          duplicate_of: action.payload.ai_duplicate_of,
          duplicate_rationale:
            action.payload.ai_duplicate_rationale,
        };
      })

      // Pending requests
      .addMatcher(
        (action) =>
          action.type.startsWith("ai/") &&
          action.type.endsWith("/pending"),
        (state) => {
          state.status = "loading";
          state.error = null;
        }
      )

      // Failed requests
      .addMatcher(
        (action) =>
          action.type.startsWith("ai/") &&
          action.type.endsWith("/rejected"),
        (state, action) => {
          state.status = "failed";
          state.error =
            action.error?.message || "AI Copilot request failed";
        }
      );
  },
});

export const { clearAiResult } = aiSlice.actions;
export default aiSlice.reducer;