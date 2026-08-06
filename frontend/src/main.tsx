import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import { QueryClientProvider } from '@tanstack/react-query';

import '@fontsource-variable/manrope/wght.css';

import App from '@/App';
import { queryClient } from '@/app/query-client';
import { AppToaster } from '@/components/feedback/app-toaster';
import '@/index.css';
import { ThemeProvider } from '@/theme/theme-provider';

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <ThemeProvider>
            <QueryClientProvider client={queryClient}>
                <App />
            </QueryClientProvider>

            <AppToaster />
        </ThemeProvider>
    </StrictMode>,
);
