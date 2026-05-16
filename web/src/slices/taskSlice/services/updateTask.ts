import { AxiosError } from 'axios';

import { notifications } from '@mantine/notifications';
import { createAsyncThunk } from '@reduxjs/toolkit';

import type { Task, TaskFormValues } from '../types';
import type { ThunkConfig } from '@/store';
type Props = {
  taskId: number;
  task: Partial<TaskFormValues>;
};

export const updateTask = createAsyncThunk<Task, Props, ThunkConfig<string>>(
  'task/updateTask',
  async ({ taskId, task }, { rejectWithValue, extra }) => {
    const {
      name,
      description,
      is_active,
      url,
      http_method,
      timeout,
      expected_status_code,
      sla_target,
      check_interval_seconds,
      cron_expression,
      responsible_persons,
    } = task;

    try {
      const { data } = await extra.api.put<Task>(
        `/monitoring-tasks/${taskId}/`,
        {
          name,
          description,
          is_active,
          url,
          http_method,
          timeout,
          expected_status_code,
          sla_target,
          check_interval_seconds,
          cron_expression,
          headers: task.headers ? JSON.parse(task.headers) : undefined,
          body: task.body ? JSON.parse(task.body) : undefined,
          responsible_persons: responsible_persons?.map(
            ({ id, name, email }) => ({
              id,
              name,
              email,
            }),
          ),
        },
      );

      if (!data) {
        throw new Error();
      }

      notifications.show({
        title: 'Сохранение',
        message: 'Параметры задачи мониторинга успешно сохранены',
      });

      return data;
    } catch (e) {
      const message =
        e instanceof AxiosError && e.response?.data?.detail?.[0]?.msg
          ? e.response.data.detail[0].msg
          : 'Unknown error';

      notifications.show({
        message,
        title: 'Сохранение',
        color: 'pink',
      });

      return rejectWithValue(message);
    }
  },
);
