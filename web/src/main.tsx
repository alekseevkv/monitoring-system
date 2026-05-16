import '@mantine/core/styles.css';
import '@mantine/notifications/styles.css';
import './index.css';

import { createRoot } from 'react-dom/client';
import { Provider as StoreProvider } from 'react-redux';
import { BrowserRouter } from 'react-router';

import { App } from '@/App';
import { store } from '@/store';
import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';

createRoot(document.getElementById('root')!).render(
  <StoreProvider store={store}>
    <MantineProvider>
      <BrowserRouter>
        <App />
        <Notifications />
      </BrowserRouter>
    </MantineProvider>
  </StoreProvider>,
);
