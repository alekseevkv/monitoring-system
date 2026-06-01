import { AxiosError } from 'axios';

import { createAsyncThunk } from '@reduxjs/toolkit';

import type { TaskMetrics } from '../types';
import type { ThunkConfig } from '@/store';

type Props = {
  taskId: number;
  month?: string;
};

export const fetchTaskMetrics = createAsyncThunk<
  TaskMetrics,
  Props,
  ThunkConfig<string>
>(
  'report/fetchTaskMetrics',
  async ({ taskId, month }, { rejectWithValue, extra }) => {
    try {
      const { data } = await extra.api.get<TaskMetrics>(`/sla/${taskId}/`, {
        params: { month },
      });

      if (!data) {
        throw new Error();
      }

      return data;
    } catch (e) {
      return rejectWithValue(
        e instanceof AxiosError && e.response?.data?.message
          ? e.response.data.message
          : 'Unknown error',
      );
    }
  },
);
