import { createSlice } from '@reduxjs/toolkit';

import { fetchTasks } from './services/fetchTasks';

import type { PayloadAction } from '@reduxjs/toolkit';
import type { TaskSchema } from './types';
const initialState: TaskSchema = {
  tasks: [],
  tasksLoading: false,
  tasksError: null,
};

export const taskSlice = createSlice({
  name: 'task',
  initialState,
  reducers: {
    setTasks: (state, { payload }: PayloadAction<TaskSchema['tasks']>) => {
      state.tasks = payload;
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchTasks.pending, (state) => {
      state.tasksError = null;
      state.tasksLoading = true;
    });
    builder.addCase(fetchTasks.fulfilled, (state, action) => {
      state.tasksLoading = false;
      state.tasks = action.payload;
    });
    builder.addCase(fetchTasks.rejected, (state, action) => {
      state.tasksLoading = false;
      state.tasksError = action.payload ?? null;
    });
  },
});

export const { actions: taskActions, reducer: taskReducer } = taskSlice;
