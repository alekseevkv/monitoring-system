import { createSlice } from '@reduxjs/toolkit';

import { fetchIncidents } from './services/fetchIncidents';
import { fetchUptimeReport } from './services/fetchUptimeReport';

import type { ReportSchema } from './types';
import type { PayloadAction } from '@reduxjs/toolkit';
const initialState: ReportSchema = {
  incidents: [],
  incidentsLoading: false,
  incidentsError: null,
  uptimeReport: [],
  uptimeReportLoading: false,
  uptimeReportError: null,
};

export const reportSlice = createSlice({
  name: 'report',
  initialState,
  reducers: {
    setIncidentsReport: (
      state,
      { payload }: PayloadAction<ReportSchema['incidents']>,
    ) => {
      state.incidents = payload;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchIncidents.pending, (state) => {
      state.incidentsError = null;
      state.incidentsLoading = true;
    });
    builder.addCase(fetchIncidents.fulfilled, (state, action) => {
      state.incidentsLoading = false;
      state.incidents = action.payload?.items;
    });
    builder.addCase(fetchIncidents.rejected, (state, action) => {
      state.incidentsLoading = false;
      state.incidentsError = action.payload ?? null;
    });
    builder.addCase(fetchUptimeReport.pending, (state) => {
      state.uptimeReportError = null;
      state.uptimeReportLoading = true;
    });
    builder.addCase(fetchUptimeReport.fulfilled, (state, action) => {
      state.uptimeReportLoading = false;
      state.uptimeReport = action.payload?.items;
    });
    builder.addCase(fetchUptimeReport.rejected, (state, action) => {
      state.uptimeReportLoading = false;
      state.uptimeReportError = action.payload ?? null;
    });
  },
});

export const { actions: reportActions, reducer: reportReducer } = reportSlice;
