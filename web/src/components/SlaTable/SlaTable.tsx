import { Link } from 'react-router';

import { useAppSelector } from '@/hook';
import { getReportSla } from '@/slices/reportSlice/selectors';
import { getMonthName } from '@/utils';
import { Anchor, Table } from '@mantine/core';

import type { SlaReportItem } from '@/slices/reportSlice/types';
export const SlaTable = () => {
  const slaData = useAppSelector(getReportSla);
  const columnsCount = slaData.months.length + 1;

  return (
    <Table striped>
      <Table.Thead>
        <Table.Tr>
          {['Сервис', ...slaData.months.map((m) => getMonthName(m))].map(
            (clmName, idx) => (
              <Table.Th
                key={`${clmName}-${idx}`}
                styles={{ th: { textTransform: 'capitalize' } }}
              >
                {clmName}
              </Table.Th>
            ),
          )}
        </Table.Tr>
      </Table.Thead>
      <Table.Tbody>
        {slaData.items.map((item) => (
          <Table.Tr key={item.id}>
            {new Array(columnsCount).fill(null).map((_, idx) => {
              return (
                <Table.Td key={`${item.name}-${idx}`}>
                  {idx === 0 ? (
                    <Anchor
                      component={Link}
                      to={`/report/${item.id}/`}
                      underline="never"
                      fz={14}
                    >
                      {item.name}
                    </Anchor>
                  ) : (
                    (
                      item[`month_${idx}` as keyof SlaReportItem] as number
                    ).toFixed(3)
                  )}
                </Table.Td>
              );
            })}
          </Table.Tr>
        ))}
      </Table.Tbody>
    </Table>
  );
};
