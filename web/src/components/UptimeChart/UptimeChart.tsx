import { useMemo } from 'react';

import { useAppSelector } from '@/hook';
import { getReportUptime } from '@/slices/reportSlice/selectors';
import { BarsList } from '@mantine/charts';

export const UptimeChart = () => {
  const report = useAppSelector(getReportUptime);

  const data = useMemo(() => {
    return report
      .toSorted((a, b) => (b.uptime_s ?? 0) - (a.uptime_s ?? 0))
      .map(({ monitoring_task_name, uptime_s }) => ({
        name: monitoring_task_name,
        value: uptime_s ? Math.round(uptime_s) : 0,
      }));
  }, [report]);

  return (
    <BarsList
      data={data}
      barsLabel="Наименование сервиса"
      valueLabel="Uptime, сек"
      valueFormatter={(value) => value.toLocaleString()}
      styles={{ barLabel: { whiteSpace: 'nowrap' } }}
      getBarProps={(barData) => ({
        style: {
          color: barData.value === 0 ? '#e64980' : '#1864ab',
        },
      })}
    />
  );
};
