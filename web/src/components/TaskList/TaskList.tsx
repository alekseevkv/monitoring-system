import { TaskItem } from '@/components/TaskItem/TaskItem';
import { useAppSelector } from '@/hook';
import { getTasks } from '@/slices/taskSlice/selectors';

import classes from './TaskList.module.css';

export const TaskList = () => {
  const taskItems = useAppSelector(getTasks);

  return (
    <div className={classes.container}>
      {taskItems.map(({ id, name }) => (
        <TaskItem key={id} id={id} name={name} />
      ))}
    </div>
  );
};
