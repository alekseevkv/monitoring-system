import { useEffect } from 'react';
import { Link } from 'react-router';

import { TaskList } from '@/components/TaskList/TaskList';
import { useAppDispatch } from '@/hook';
import { fetchTasks } from '@/slices/taskSlice/services/fetchTasks';
import { Button } from '@mantine/core';

import classes from './TaskListPage.module.css';

export const TaskListPage = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchTasks());
  }, [dispatch]);

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <div className={classes.title}>Сервисы мониторинга</div>
        <TaskList />
        <div className={classes.addButton}>
          <Button component={Link} to="/tasks/new/">
            Добавить сервис
          </Button>
        </div>
      </div>
    </div>
  );
};
