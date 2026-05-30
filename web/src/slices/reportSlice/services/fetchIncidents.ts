import { AxiosError } from 'axios';

import { createAsyncThunk } from '@reduxjs/toolkit';

import type { Incident } from '../types';
import type { ThunkConfig } from '@/store';
export const fetchIncidents = createAsyncThunk<
  { items: Incident[] },
  undefined,
  ThunkConfig<string>
>('report/fetchIncidents', async (_, { rejectWithValue, extra }) => {
  try {
    const { data } = await extra.api.get<{ items: Incident[] }>(
      '/open-incidents',
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
