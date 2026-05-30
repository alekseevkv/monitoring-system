import { api } from '@/api';
import { reportReducer } from '@/slices/reportSlice/reportSlice';
import { taskReducer } from '@/slices/taskSlice/taskSlice';
import { configureStore } from '@reduxjs/toolkit';

import type { AxiosInstance } from 'axios';
const extraArg: ThunkExtraArg = {
  api,
};

export const store = configureStore({
  reducer: {
    task: taskReducer,
    report: reportReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      thunk: {
        extraArgument: extraArg,
      },
      serializableCheck: false,
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export interface ThunkExtraArg {
  api: AxiosInstance;
}

export interface ThunkConfig<T> {
  rejectValue: T;
  extra: ThunkExtraArg;
  state: RootState;
}
