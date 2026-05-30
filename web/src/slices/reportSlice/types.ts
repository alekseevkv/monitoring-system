export type Incident = {
  id: number;
  status: 'открыт' | 'закрыт';
  started_at: string;
  started_by_check_id: number;
  description: string;
  monitoring_task_id: number;
  monitoring_task_name: string;
  monitoring_task_method: string;
};

export type UptimeReportItem = {
  monitoring_task_id: number;
  monitoring_task_name: string;
  monitoring_task_method: string;
  is_incident: boolean;
  uptime_s: number;
  incident_duration_s: number;
};

export type SlaReportItem = {
  id: number;
  name: string;
  month_1: number;
  month_2: number;
  month_3: number;
  month_4: number;
  month_5: number;
  month_6: number;
  month_7: number;
  month_8: number;
  month_9: number;
  month_10: number;
  month_11: number;
  month_12: number;
};

export type SlaReport = {
  months: string[];
  items: SlaReportItem[];
};

export type TaskMetrics = {
  id: number;
  name: string;
  sla_month: number;
  successful_checks: number;
  failed_checks: number;
  total_checks: number;
  success_rate: number;
  incident_count: number;
  total_downtime_seconds: number;
  total_uptime_seconds: number;
  avg_response_time_s: number;
  min_response_time_s: number;
  max_response_time_s: number;
  achieved_target: boolean;
};

export type ReportSchema = {
  incidents: Incident[];
  incidentsLoading: boolean;
  incidentsError: string | null;
  uptimeReport: UptimeReportItem[];
  uptimeReportLoading: boolean;
  uptimeReportError: string | null;
  slaReport: SlaReport;
  slaReportLoading: boolean;
  slaReportError: string | null;
  taskMetrics: TaskMetrics | null;
  taskMetricsLoading: boolean;
  taskMetricsError: string | null;
};
