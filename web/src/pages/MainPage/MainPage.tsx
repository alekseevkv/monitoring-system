import { useEffect } from 'react';

import { IncidentsTable } from '@/components/IncidentsTable/IncidentsTable';
import { useAppDispatch } from '@/hook';
import { fetchIncidents } from '@/slices/reportSlice/services/fetchIncidents';

import classes from './MainPage.module.css';

export const MainPage = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchIncidents());
  }, [dispatch]);

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <div>
          <div className={classes.title}>Открытые инциденты</div>
          <IncidentsTable />
        </div>
      </div>
    </div>
  );
};
