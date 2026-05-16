import { createSlice } from '@reduxjs/toolkit';

import { fetchTask } from './services/fetchTask';
import { fetchTasks } from './services/fetchTasks';
import { updateTask } from './services/updateTask';

import type { PayloadAction } from '@reduxjs/toolkit';
import type { TaskSchema } from './types';
const initialState: TaskSchema = {
  tasks: [],
  tasksLoading: false,
  tasksError: null,
  task: null,
  taskLoading: false,
  taskError: null,
};

export const taskSlice = createSlice({
  name: 'task',
  initialState,
  reducers: {
    setTasks: (state, { payload }: PayloadAction<TaskSchema['tasks']>) => {
      state.tasks = payload;
    },
    setTask: (state, { payload }: PayloadAction<TaskSchema['task'] | null>) => {
      state.task = payload;
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
    builder.addCase(fetchTask.pending, (state) => {
      state.taskError = null;
      state.taskLoading = true;
      state.task = null;
    });
    builder.addCase(fetchTask.fulfilled, (state, action) => {
      state.taskLoading = false;
      state.task = action.payload;
    });
    builder.addCase(fetchTask.rejected, (state, action) => {
      state.taskLoading = false;
      state.taskError = action.payload ?? null;
    });
    builder.addCase(updateTask.pending, (state) => {
      state.taskError = null;
      state.taskLoading = true;
    });
    builder.addCase(updateTask.fulfilled, (state, action) => {
      state.taskLoading = false;
      state.task = action.payload;
    });
    builder.addCase(updateTask.rejected, (state, action) => {
      state.taskLoading = false;
      state.taskError = action.payload ?? null;
    });
  },
});

export const { actions: taskActions, reducer: taskReducer } = taskSlice;
