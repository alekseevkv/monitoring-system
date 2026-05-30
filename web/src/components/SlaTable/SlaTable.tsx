import { useMemo } from 'react';

import { useAppSelector } from '@/hook';
import { getReportSla } from '@/slices/reportSlice/selectors';
import { getMonthName } from '@/utils';
import { Table } from '@mantine/core';

import type { TableData } from '@mantine/core';
import type { SlaReportItem } from '@/slices/reportSlice/types';
export const SlaTable = () => {
  const slaData = useAppSelector(getReportSla);

  const tableData = useMemo(() => {
    const columnsCount = slaData.months.length + 1;

    return slaData.items.reduce<TableData>(
      (acc, item) => {
        acc.body?.push(
          new Array(columnsCount).fill(null).map((_, idx) => {
            return idx === 0
              ? item.name
              : (item[`month_${idx}` as keyof SlaReportItem] as number).toFixed(
                  3,
                );
          }),
        );
        return acc;
      },
      {
        head: ['Сервис', ...slaData.months.map((m) => getMonthName(m))],
        body: [],
      },
    );
  }, [slaData.items, slaData.months]);

  return <Table striped data={tableData} />;
};
