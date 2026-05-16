import { useNavigate } from 'react-router';

import { useAppDispatch } from '@/hook';
import { deleteTask } from '@/slices/taskSlice/services/deleteTask';
import { fetchTasks } from '@/slices/taskSlice/services/fetchTasks';
import { ActionIcon, Card, Group, Text } from '@mantine/core';
import { TrashIcon } from '@phosphor-icons/react';

import type { Task } from '@/slices/taskSlice/types';
type Props = {
  id: Task['id'];
  name: Task['name'];
};

export const TaskItem = ({ id, name }: Props) => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();

  return (
    <Card
      withBorder
      shadow="xs"
      padding="xs"
      orientation="horizontal"
      onClick={() => {
        navigate(`/tasks/${id}/`);
      }}
      styles={{ root: { cursor: 'pointer' } }}
    >
      <Group justify="space-between" w="100%">
        <Text fw={500} truncate="end">
          {name}
        </Text>
        <ActionIcon
          variant="subtle"
          size="md"
          onClick={(e) => {
            e.stopPropagation();
            dispatch(deleteTask({ taskId: id })).then(({ meta }) => {
              if (meta.requestStatus === 'fulfilled') {
                dispatch(fetchTasks());
              }
            });
          }}
        >
          <TrashIcon style={{ width: '70%', height: '70%' }} />
        </ActionIcon>
      </Group>
    </Card>
  );
};
