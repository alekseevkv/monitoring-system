import { Route, Routes } from 'react-router';

import { Layout } from '@/components/Layout/Layout';
import { MainPage } from '@/pages/MainPage/MainPage';
import { ReportPage } from '@/pages/ReportPage/ReportPage';
import { TasksPage } from '@/pages/TasksPage/TasksPage';

export const App = () => {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<MainPage />} />
        <Route path="tasks" element={<TasksPage />} />
        <Route path="report" element={<ReportPage />} />
      </Route>
    </Routes>
  );
};
