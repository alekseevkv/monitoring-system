import { useEffect } from 'react';

import { TaskList } from '@/components/TaskList/TaskList';
import { useAppDispatch } from '@/hook';
import { fetchTasks } from '@/slices/taskSlice/services/fetchTasks';
import { Button } from '@mantine/core';

import classes from './TasksPage.module.css';

export const TasksPage = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchTasks());
  }, [dispatch]);

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <TaskList />
        <div className={classes.addButton}>
          <Button
            // loading={}
            onClick={() => {}}
          >
            Добавить сервис
          </Button>
        </div>
      </div>
    </div>
  );
};
