import { TaskForm } from '@/components/TaskForm/TaskForm';

import classes from './NewTaskPage.module.css';

import type { TaskFormValues } from '@/slices/taskSlice/types';

const task: TaskFormValues = {
  name: '',
  is_active: true,
  url: '',
  http_method: 'GET',
  timeout: 30,
  expected_status_code: 200,
  sla_target: 99.9,
  check_interval_seconds: 300,
  responsible_persons: [],
};

export const NewTaskPage = () => {
  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <div className={classes.title}>Параметры сервиса</div>
        <TaskForm initialValues={task} />
      </div>
    </div>
  );
};
