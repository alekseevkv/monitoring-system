import { AxiosError } from 'axios';

import { notifications } from '@mantine/notifications';
import { createAsyncThunk } from '@reduxjs/toolkit';

import type { ThunkConfig } from '@/store';
type Props = {
  taskId: number;
};

export const deleteTask = createAsyncThunk<
  undefined,
  Props,
  ThunkConfig<string>
>('task/deleteTask', async ({ taskId }, { rejectWithValue, extra }) => {
  try {
    await extra.api.delete(`/monitoring-tasks/${taskId}/`);

    notifications.show({
      title: 'Удаление',
      message: 'Сервис мониторинга успешно удален',
    });
  } catch (e) {
    const message =
      e instanceof AxiosError && e.response?.data?.detail?.[0]?.msg
        ? e.response.data.detail[0].msg
        : 'Unknown error';

    notifications.show({
      message,
      title: 'Удаление',
      color: 'pink',
    });

    return rejectWithValue(message);
  }
});
