import '@mantine/core/styles.css';
import './index.css';

import { createRoot } from 'react-dom/client';
import { Provider as StoreProvider } from 'react-redux';
import { BrowserRouter } from 'react-router';

import { App } from '@/App';
import { store } from '@/store';
import { MantineProvider } from '@mantine/core';

createRoot(document.getElementById('root')!).render(
  <StoreProvider store={store}>
    <MantineProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </MantineProvider>
  </StoreProvider>,
);
