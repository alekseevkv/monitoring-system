import { useEffect } from 'react';

import { SlaTable } from '@/components/SlaTable/SlaTable';
import { useAppDispatch } from '@/hook';
import { fetchSlaReport } from '@/slices/reportSlice/services/fetchSlaReport';

import classes from './ReportPage.module.css';

export const ReportPage = () => {
  const dispatch = useAppDispatch();

  useEffect(() => {
    dispatch(fetchSlaReport());
  }, [dispatch]);

  return (
    <div className={classes.container}>
      <div className={classes.content}>
        <div className={classes.title}>Сводный отчет</div>
        <SlaTable />
      </div>
    </div>
  );
};
