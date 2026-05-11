import { Link, NavLink as RouterNavLink, useMatch } from 'react-router';

import { Anchor, NavLink } from '@mantine/core';
import { HeartbeatIcon } from '@phosphor-icons/react';

import classes from './Header.module.css';

export const Header = () => {
  const isTasksPage = useMatch('/tasks');
  const isReportPage = useMatch('/report');

  return (
    <header className={classes.header}>
      <div className={classes.titleWrapper}>
        <HeartbeatIcon size={20} />
        <Anchor
          component={Link}
          to="/"
          underline="never"
          className={classes.title}
        >
          Система мониторинга сервисов
        </Anchor>
      </div>
      <div className={classes.navbar}>
        <NavLink
          component={RouterNavLink}
          to="/tasks"
          label="Сервисы мониторинга"
          variant="subtle"
          active={Boolean(isTasksPage)}
          className={classes.link}
        />
        <NavLink
          component={RouterNavLink}
          to="/report"
          label="Сводный отчет"
          variant="subtle"
          active={Boolean(isReportPage)}
          className={classes.link}
        />
      </div>
    </header>
  );
};
