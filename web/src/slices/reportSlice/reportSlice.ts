import { fetchTaskMetrics } from '@/slices/reportSlice/services/fetchTaskMetrics';
import { createSlice } from '@reduxjs/toolkit';

import { fetchIncidents } from './services/fetchIncidents';
import { fetchSlaReport } from './services/fetchSlaReport';
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
  slaReport: {
    months: [],
    items: [],
  },
  slaReportLoading: false,
  slaReportError: null,
  taskMetrics: null,
  taskMetricsLoading: false,
  taskMetricsError: null,
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
    builder.addCase(fetchSlaReport.pending, (state) => {
      state.slaReportError = null;
      state.slaReportLoading = true;
    });
    builder.addCase(fetchSlaReport.fulfilled, (state, action) => {
      state.slaReportLoading = false;
      state.slaReport = action.payload;
    });
    builder.addCase(fetchSlaReport.rejected, (state, action) => {
      state.slaReportLoading = false;
      state.slaReportError = action.payload ?? null;
    });
    builder.addCase(fetchTaskMetrics.pending, (state) => {
      state.taskMetricsError = null;
      state.taskMetricsLoading = true;
    });
    builder.addCase(fetchTaskMetrics.fulfilled, (state, action) => {
      state.taskMetricsLoading = false;
      state.taskMetrics = action.payload;
    });
    builder.addCase(fetchTaskMetrics.rejected, (state, action) => {
      state.taskMetricsLoading = false;
      state.taskMetricsError = action.payload ?? null;
    });
  },
});

export const { actions: reportActions, reducer: reportReducer } = reportSlice;
