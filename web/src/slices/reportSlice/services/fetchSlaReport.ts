import { AxiosError } from 'axios';

import { createAsyncThunk } from '@reduxjs/toolkit';

import type { SlaReport } from '../types';
import type { ThunkConfig } from '@/store';
export const fetchSlaReport = createAsyncThunk<
  SlaReport,
  undefined,
  ThunkConfig<string>
>('report/fetchSlaReport', async (_, { rejectWithValue, extra }) => {
  try {
    const { data } = await extra.api.get<SlaReport>('/sla/');

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
