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

export type ReportSchema = {
  incidents: Incident[];
  incidentsLoading: boolean;
  incidentsError: string | null;
  uptimeReport: UptimeReportItem[];
  uptimeReportLoading: boolean;
  uptimeReportError: string | null;
};
