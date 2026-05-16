import { useEffect } from 'react';
import { useParams } from 'react-router';

import { TaskForm } from '@/components/TaskForm/TaskForm';
import { useAppDispatch, useAppSelector } from '@/hook';
import { getTask } from '@/slices/taskSlice/selectors';
import { fetchTask } from '@/slices/taskSlice/services/fetchTask';
import { taskActions } from '@/slices/taskSlice/taskSlice';

import classes from './TaskPage.module.css';

export const TaskPage = () => {
  const { tid } = useParams();
  const taskId = Number(tid);
  const dispatch = useAppDispatch();
  const task = useAppSelector(getTask);

  useEffect(() => {
    if (taskId) {
      dispatch(fetchTask(taskId));
    }
  }, [dispatch, taskId]);

  useEffect(() => {
    return () => {
      dispatch(taskActions.setTask(null));
    };
  }, [dispatch]);

  if (!task) return null;

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <TaskForm taskId={taskId} initialValues={task} />
      </div>
    </div>
  );
};
