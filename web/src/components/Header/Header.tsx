import { Link, NavLink as RouterNavLink } from 'react-router';

import { Anchor, NavLink } from '@mantine/core';
import { HeartbeatIcon } from '@phosphor-icons/react';

import classes from './Header.module.css';

export const Header = () => {
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
          to="/tasks/"
          label="Сервисы мониторинга"
          variant="subtle"
          end
          className={classes.link}
        />
        <NavLink
          component={RouterNavLink}
          to="/report/"
          label="Сводный отчет"
          variant="subtle"
          end
          className={classes.link}
        />
      </div>
    </header>
  );
};
