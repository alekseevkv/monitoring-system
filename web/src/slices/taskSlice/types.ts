export type Task = {
  id: number;
  name: string;
  is_active: boolean;
  url: string;
  http_method: string;
  timeout: number;
  expected_status_code: number;
  sla_target: number;
  check_interval_seconds: number;
  responsible_persons: string[];
  notification_emails: string[];
  created_at: string;
  updated_at: string;
  headers?: Record<string, string>;
  description?: string;
  cron_expression?: string;
};

export type TaskSchema = {
  tasks: Task[];
  tasksLoading: boolean;
  tasksError: string | null;
};
