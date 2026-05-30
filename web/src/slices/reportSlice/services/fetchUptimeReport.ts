import { AxiosError } from 'axios';

import { createAsyncThunk } from '@reduxjs/toolkit';

import type { UptimeReportItem } from '../types';
import type { ThunkConfig } from '@/store';
export const fetchUptimeReport = createAsyncThunk<
  { items: UptimeReportItem[] },
  undefined,
  ThunkConfig<string>
>('report/fetchUptimeReport', async (_, { rejectWithValue, extra }) => {
  try {
    const { data } = await extra.api.get<{ items: UptimeReportItem[] }>(
      '/uptime',
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
});
