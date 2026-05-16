export type ResponsiblePerson = {
  id: number;
  name: string;
  email: string;
  created_at: string;
  updated_at: string;
};

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
  created_at: string;
  updated_at: string;
  responsible_persons: ResponsiblePerson[];
  headers?: Record<string, string>;
  body?: Record<string, string>;
  description?: string;
  cron_expression?: string;
};

export type TaskSchema = {
  tasks: Task[];
  tasksLoading: boolean;
  tasksError: string | null;
  task: Task | null;
  taskLoading: boolean;
  taskError: string | null;
};

export type TaskFormValues = Omit<
  Task,
  | 'id'
  | 'created_at'
  | 'updated_at'
  | 'headers'
  | 'body'
  | 'responsible_persons'
> & {
  headers?: string;
  body?: string;
  responsible_persons: {
    name: string;
    email: string;
    id?: number;
    key?: string;
  }[];
};
