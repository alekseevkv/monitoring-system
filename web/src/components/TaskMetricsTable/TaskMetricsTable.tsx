import type { TaskMetrics } from '@/slices/reportSlice/types';
import { formatNumber } from '@/utils';
import { Table } from '@mantine/core';

type Props = {
  taskMetrics: TaskMetrics;
};

export const TaskMetricsTable = ({ taskMetrics }: Props) => {
  return (
    <Table variant="vertical" layout="fixed">
      <Table.Tbody>
        <Table.Tr>
          <Table.Th w={320}>Проверки</Table.Th>
          <Table.Td>
            {formatNumber(taskMetrics.total_checks, {
              fractionDigits: 0,
            })}
          </Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Неудачные проверки</Table.Th>
          <Table.Td>
            {formatNumber(taskMetrics.failed_checks, {
              fractionDigits: 0,
            })}
          </Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Успешные проверки</Table.Th>
          <Table.Td>
            {formatNumber(taskMetrics.successful_checks, {
              fractionDigits: 0,
            })}
          </Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Процент успешных проверок</Table.Th>
          <Table.Td>{formatNumber(taskMetrics.success_rate)}</Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Инциденты</Table.Th>
          <Table.Td>
            {formatNumber(taskMetrics.incident_count, {
              fractionDigits: 0,
            })}
          </Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Общее время простоя, сек</Table.Th>
          <Table.Td>
            {formatNumber(taskMetrics.total_downtime_seconds)}
          </Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Общее время бесперебойной работы, сек</Table.Th>
          <Table.Td>{formatNumber(taskMetrics.total_uptime_seconds)}</Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Среднее время ответа, сек</Table.Th>
          <Table.Td>{formatNumber(taskMetrics.avg_response_time_s)}</Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Минимальное время ответа, сек</Table.Th>
          <Table.Td>{formatNumber(taskMetrics.min_response_time_s)}</Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Максимальное время ответа, сек</Table.Th>
          <Table.Td>{formatNumber(taskMetrics.max_response_time_s)}</Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Доступность</Table.Th>
          <Table.Td>{formatNumber(taskMetrics.sla_month)}</Table.Td>
        </Table.Tr>
        <Table.Tr>
          <Table.Th>Достигнута целевая доступность</Table.Th>
          <Table.Td>{taskMetrics.achieved_target ? 'Да' : 'Нет'}</Table.Td>
        </Table.Tr>
      </Table.Tbody>
    </Table>
  );
};
