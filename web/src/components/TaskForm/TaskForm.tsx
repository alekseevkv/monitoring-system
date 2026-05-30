import type { Task, TaskFormValues } from '@/slices/taskSlice/types';
import { useNavigate } from 'react-router';

import { useAppDispatch, useAppSelector } from '@/hook';
import { getTaskLoading } from '@/slices/taskSlice/selectors';
import { createTask } from '@/slices/taskSlice/services/createTask';
import { updateTask } from '@/slices/taskSlice/services/updateTask';
import {
    ActionIcon, Button, Fieldset, Group, JsonInput, NumberInput, Stack, Switch, Textarea, TextInput
} from '@mantine/core';
import { hasLength, isInRange, isUrl, matches, useForm } from '@mantine/form';
import { randomId } from '@mantine/hooks';
import { TrashIcon } from '@phosphor-icons/react';

import classes from './TaskForm.module.css';

type Props = {
  initialValues: Task | TaskFormValues;
  taskId?: number;
};

export const TaskForm = ({ taskId, initialValues }: Props) => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const loading = useAppSelector(getTaskLoading);

  const form = useForm<TaskFormValues>({
    mode: 'uncontrolled',
    initialValues: {
      ...initialValues,
      responsible_persons: [
        ...(initialValues.responsible_persons ?? []).map((person) => ({
          ...person,
        })),
      ],
      headers: initialValues.headers
        ? JSON.stringify(initialValues.headers)
        : undefined,
      body: initialValues.body ? JSON.stringify(initialValues.body) : undefined,
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

  const responsiblePersonfields = form
    .getValues()
    .responsible_persons.map((item, index) => (
      <Group key={item.id ?? item.key} align="flex-end">
        <div className={classes.inputWrapper}>
          <TextInput
            withAsterisk
            label="ФИО"
            key={form.key(`responsible_persons.${index}.name`)}
            {...form.getInputProps(`responsible_persons.${index}.name`)}
          />
        </div>
        <div className={classes.inputWrapper}>
          <TextInput
            withAsterisk
            label="Email"
            key={form.key(`responsible_persons.${index}.email`)}
            {...form.getInputProps(`responsible_persons.${index}.email`)}
          />
        </div>
        <ActionIcon
          variant="subtle"
          size="md"
          mb="4px"
          onClick={() => form.removeListItem('responsible_persons', index)}
        >
          <TrashIcon style={{ width: '70%', height: '70%' }} />
        </ActionIcon>
      </Group>
    ));

  return (
    <form
      onSubmit={form.onSubmit((values) => {
        if (taskId) {
          dispatch(updateTask({ taskId, task: values }));
        } else {
          dispatch(createTask({ task: values })).then(({ meta }) => {
            if (meta.requestStatus === 'fulfilled') {
              navigate(`/tasks/`);
            }
          });
        }
      })}
    >
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
          <Group>
            <div className={classes.inputWrapper}>
              <JsonInput
                autosize
                formatOnBlur
                label="Кастомные HTTP-заголовки"
                minRows={3}
                key={form.key('headers')}
                {...form.getInputProps('headers')}
              />
            </div>
            <div className={classes.inputWrapper}>
              <JsonInput
                autosize
                formatOnBlur
                label="Тело запроса"
                minRows={3}
                key={form.key('body')}
                {...form.getInputProps('body')}
              />
            </div>
          </Group>
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
        <Fieldset legend="Ответственные">
          <Stack gap="6px">
            {responsiblePersonfields}
            <Group mt="md" justify="flex-end">
              <Button
                onClick={() =>
                  form.insertListItem('responsible_persons', {
                    name: '',
                    email: '',
                    key: randomId(),
                  })
                }
              >
                Добавить
              </Button>
            </Group>
          </Stack>
        </Fieldset>
      </Stack>

      <div className={classes.saveButton}>
        <Button type="submit" disabled={loading}>
          {taskId ? 'Сохранить' : 'Создать'}
        </Button>
      </div>
    </form>
  );
};
