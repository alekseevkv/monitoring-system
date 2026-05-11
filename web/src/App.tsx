import { Route, Routes } from 'react-router';

import { Layout } from '@/components/Layout/Layout';

export const App = () => {
  return (
    <Routes>
      <Route element={<Layout />}></Route>
    </Routes>
  );
};
