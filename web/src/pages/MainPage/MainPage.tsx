import { useEffect } from 'react';

import { IncidentsTable } from '@/components/IncidentsTable/IncidentsTable';
import { UptimeChart } from '@/components/UptimeChart/UptimeChart';
import { useAppDispatch } from '@/hook';
import { fetchIncidents } from '@/slices/reportSlice/services/fetchIncidents';
import { fetchUptimeReport } from '@/slices/reportSlice/services/fetchUptimeReport';

import classes from './MainPage.module.css';

export const MainPage = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchIncidents());
    dispatch(fetchUptimeReport());
  }, [dispatch]);

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <div>
          <div className={classes.title}>Открытые инциденты</div>
          <IncidentsTable />
        </div>
        <div className={classes.uptimeReportContainer}>
          <div className={classes.title}>
            Текущее время бесперебойной работы
          </div>
          <UptimeChart />
        </div>
      </div>
    </div>
  );
};
