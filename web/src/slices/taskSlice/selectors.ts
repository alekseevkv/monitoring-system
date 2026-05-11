import type { RootState } from '@/store';

export const getTasks = (state: RootState) => state.task.tasks;
export const getTask = (state: RootState) => state.task.task;
