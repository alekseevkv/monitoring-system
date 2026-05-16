import { AxiosError } from 'axios';

import { notifications } from '@mantine/notifications';
import { createAsyncThunk } from '@reduxjs/toolkit';

import type { Task, TaskFormValues } from '../types';
import type { ThunkConfig } from '@/store';
type Props = {
  task: TaskFormValues;
};

export const createTask = createAsyncThunk<Task, Props, ThunkConfig<string>>(
  'task/createTask',
  async ({ task }, { rejectWithValue, extra }) => {
    const {
      name,
      description,
      is_active,
      url,
      http_method,
      headers,
      body,
      timeout,
      expected_status_code,
      sla_target,
      check_interval_seconds,
      cron_expression,
      responsible_persons,
    } = task;

    try {
      const { data } = await extra.api.post<Task>(`/monitoring-tasks/`, {
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
        headers: headers ? JSON.parse(headers) : undefined,
        body: body ? JSON.parse(body) : undefined,
        responsible_persons: responsible_persons?.map(
          ({ id, name, email }) => ({
            id,
            name,
            email,
          }),
        ),
      });

      if (!data) {
        throw new Error();
      }

      notifications.show({
        title: 'Добавление',
        message: 'Сервис мониторинга успешно добавлен',
      });

      return data;
    } catch (e) {
      const message =
        e instanceof AxiosError && e.response?.data?.detail?.[0]?.msg
          ? e.response.data.detail[0].msg
          : 'Unknown error';

      notifications.show({
        message,
        title: 'Добавление',
        color: 'pink',
      });

      return rejectWithValue(message);
    }
  },
);
