import type { RootState } from '@/store';

export const getReportIncidents = (state: RootState) => state.report.incidents;
export const getReportUptime = (state: RootState) => state.report.uptimeReport;
export const getReportSla = (state: RootState) => state.report.slaReport;
export const getReportTaskMetrics = (state: RootState) =>
  state.report.taskMetrics;
