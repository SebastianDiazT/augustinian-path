import { createBrowserRouter } from 'react-router';

import { RootErrorBoundary } from '@/app/errors/root-error-boundary';
import { PublicLayout } from '@/app/layouts/public-layout';
import { HomePage } from '@/pages/public/home-page';

export const router = createBrowserRouter([
    {
        path: '/',
        Component: PublicLayout,
        ErrorBoundary: RootErrorBoundary,
        children: [
            {
                index: true,
                Component: HomePage,
            },
        ],
    },
]);
