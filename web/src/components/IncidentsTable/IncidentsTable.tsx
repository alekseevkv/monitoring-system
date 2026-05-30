import { useMemo } from 'react';

import { useAppSelector } from '@/hook';
import { getReportIncidents } from '@/slices/reportSlice/selectors';
import { getTimeDifference } from '@/utils';
import { Table } from '@mantine/core';

import type { TableData } from '@mantine/core';
export const IncidentsTable = () => {
  const incidents = useAppSelector(getReportIncidents);

  const tableData = useMemo(
    () =>
      incidents.reduce<TableData>(
        (acc, { monitoring_task_name, started_at }) => {
          const { days, hours, minutes } = getTimeDifference(started_at);
          const duration = `${days} дн ${hours} ч ${minutes} мин`;
          acc.body?.push([
            monitoring_task_name,
            new Date(started_at).toLocaleDateString('ru-Ru', {
              hour: 'numeric',
              minute: 'numeric',
              second: 'numeric',
            }),
            duration,
          ]);
          return acc;
        },
        {
          head: ['Наименование сервиса', 'Время открытия', 'Длительность'],
          body: [],
        },
      ),
    [incidents],
  );

  return <Table striped data={tableData} />;
};
