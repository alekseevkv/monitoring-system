import { useNavigate } from 'react-router';

import { ActionIcon, Card, Group, Text } from '@mantine/core';
import { TrashIcon } from '@phosphor-icons/react';

import type { Task } from '@/slices/taskSlice/types';
type Props = {
  id: Task['id'];
  name: Task['name'];
};

export const TaskItem = ({ id, name }: Props) => {
  const navigate = useNavigate();

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
          }}
        >
          <TrashIcon style={{ width: '70%', height: '70%' }} />
        </ActionIcon>
      </Group>
    </Card>
  );
};
