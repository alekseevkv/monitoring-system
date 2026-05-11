import type { Task, TaskFormValues } from '@/slices/taskSlice/types';
import {
  Button,
  Fieldset,
  Group,
  JsonInput,
  NumberInput,
  Stack,
  Switch,
  Textarea,
  TextInput,
} from '@mantine/core';
import { hasLength, isInRange, isUrl, matches, useForm } from '@mantine/form';

import classes from './TaskForm.module.css';

type Props = {
  initialValues: Task;
};

export const TaskForm = ({ initialValues }: Props) => {
  const form = useForm<TaskFormValues>({
    mode: 'uncontrolled',
    initialValues: {
      ...initialValues,
      headers: initialValues.headers
        ? JSON.stringify(initialValues.headers)
        : undefined,
    },
    validate: {
      name: hasLength({ min: 1, max: 255 }, 'Имя должно быть 1-255 символов'),
      url: isUrl('Некорректный URL'),
      http_method: matches(
        /^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$/,
        'Некорректный метод запроса',
      ),
      timeout: isInRange(
        { min: 1, max: 300 },
        'Таймаут запроса должен быть от 1 до 300',
      ),
      expected_status_code: isInRange(
        { min: 100, max: 599 },
        'Код статуса ответа должен быть от 100 до 599',
      ),
      sla_target: isInRange(
        { min: 0, max: 100 },
        'Целевая доступность должна быть от 0 до 100',
      ),
      check_interval_seconds: isInRange(
        { min: 10 },
        'Интервал проверки должен быть больше или равен 10',
      ),
    },
  });

  return (
    <form onSubmit={form.onSubmit((values) => console.log(values))}>
      <Stack gap="4px">
        <Group align="flex-end">
          <div className={classes.inputWrapper}>
            <TextInput
              withAsterisk
              label="Название"
              key={form.key('name')}
              {...form.getInputProps('name')}
            />
          </div>
          <div className={classes.switch}>
            <Switch
              label="Мониторинг активен"
              key={form.key('is_active')}
              {...form.getInputProps('is_active', { type: 'checkbox' })}
            />
          </div>
        </Group>
        <Textarea
          label="Описание"
          key={form.key('description')}
          {...form.getInputProps('description')}
        />
        <Fieldset legend="Параметры HTTP-запроса">
          <TextInput
            withAsterisk
            label="URL"
            key={form.key('url')}
            {...form.getInputProps('url')}
          />
          <Group m="4px 0px">
            <div className={classes.inputWrapper}>
              <TextInput
                withAsterisk
                label="Метод"
                key={form.key('http_method')}
                {...form.getInputProps('http_method')}
              />
            </div>
            <div className={classes.inputWrapper}>
              <NumberInput
                withAsterisk
                label="Таймаут, сек."
                min={1}
                max={300}
                key={form.key('timeout')}
                {...form.getInputProps('timeout')}
              />
            </div>
            <div className={classes.inputWrapper}>
              <NumberInput
                withAsterisk
                label="Код ответа"
                min={100}
                max={599}
                key={form.key('expected_status_code')}
                {...form.getInputProps('expected_status_code')}
              />
            </div>
          </Group>
          <JsonInput
            autosize
            formatOnBlur
            label="Кастомные HTTP-заголовки"
            minRows={3}
            key={form.key('headers')}
            {...form.getInputProps('headers')}
          />
        </Fieldset>
        <Fieldset legend="SLA и расписание">
          <Group>
            <div className={classes.inputWrapper}>
              <NumberInput
                withAsterisk
                label="Целевая доступность, %"
                min={0}
                max={100}
                key={form.key('sla_target')}
                {...form.getInputProps('sla_target')}
              />
            </div>
            <div className={classes.inputWrapper}>
              <NumberInput
                withAsterisk
                label="Интервал проверки, сек."
                min={10}
                key={form.key('check_interval_seconds')}
                {...form.getInputProps('check_interval_seconds')}
              />
            </div>
            <div className={classes.inputWrapper}>
              <TextInput
                label="Cron-расписание"
                key={form.key('cron_expression')}
                {...form.getInputProps('cron_expression')}
              />
            </div>
          </Group>
        </Fieldset>
      </Stack>

      <Group mt="md" justify="flex-end">
        <Button type="submit">Сохранить</Button>
      </Group>
    </form>
  );
};
