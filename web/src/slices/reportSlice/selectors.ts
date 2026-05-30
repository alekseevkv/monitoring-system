import type { RootState } from '@/store';

export const getReportIncidents = (state: RootState) => state.report.incidents;
