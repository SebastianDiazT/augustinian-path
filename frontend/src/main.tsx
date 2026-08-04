import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import '@fontsource-variable/manrope/wght.css';

import App from './App.tsx';
import './index.css';
import { ThemeProvider } from './theme/theme-provider';

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ThemeProvider>
            <App />
        </ThemeProvider>
    </StrictMode>,
);
