import { AxiosError } from 'axios';

import { createAsyncThunk } from '@reduxjs/toolkit';

import type { Task } from '../types';
import type { ThunkConfig } from '@/store';
export const fetchTask = createAsyncThunk<Task, number, ThunkConfig<string>>(
  'task/fetchTask',
  async (taskId, { rejectWithValue, extra }) => {
    try {
      const { data } = await extra.api.get<Task>(
        `/monitoring_tasks/${taskId}/`,
      );

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
