import { Route, Routes } from 'react-router';

import { Layout } from '@/components/Layout/Layout';
import { MainPage } from '@/pages/MainPage/MainPage';
import { NewTaskPage } from '@/pages/NewTaskPage/NewTaskPage';
import { ReportPage } from '@/pages/ReportPage/ReportPage';
import { TaskListPage } from '@/pages/TaskListPage/TaskListPage';
import { TaskMetricsPage } from '@/pages/TaskMetricsPage/TaskMetricsPage';
import { TaskPage } from '@/pages/TaskPage/TaskPage';

export const App = () => {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<MainPage />} />
        <Route path="/tasks/" element={<TaskListPage />} />
        <Route path="/tasks/new/" element={<NewTaskPage />} />
        <Route path="/tasks/:tid/" element={<TaskPage />} />
        <Route path="/report/" element={<ReportPage />} />
        <Route path="/report/:tid" element={<TaskMetricsPage />} />
      </Route>
    </Routes>
  );
};
