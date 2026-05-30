import { useEffect } from 'react';
import { useParams } from 'react-router';

import { TaskMetricsTable } from '@/components/TaskMetricsTable/TaskMetricsTable';
import { useAppDispatch, useAppSelector } from '@/hook';
import { getReportTaskMetrics } from '@/slices/reportSlice/selectors';
import { fetchTaskMetrics } from '@/slices/reportSlice/services/fetchTaskMetrics';

import classes from './TaskMetricsPage.module.css';

export const TaskMetricsPage = () => {
  const { tid } = useParams();
  const taskId = Number(tid);
  const dispatch = useAppDispatch();
  const taskMetrics = useAppSelector(getReportTaskMetrics);

  useEffect(() => {
    dispatch(fetchTaskMetrics({ taskId }));
  }, [dispatch, taskId]);

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <div className={classes.title}>Метрики сервиса за предыдущий месяц</div>
        {taskMetrics && (
          <div className={classes.tableContainer}>
            <div className={classes.subTitle}>{taskMetrics.name}</div>
            <TaskMetricsTable taskMetrics={taskMetrics} />
          </div>
        )}
      </div>
    </div>
  );
};
