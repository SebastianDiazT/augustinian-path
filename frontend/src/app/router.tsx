import { createBrowserRouter } from 'react-router';

import { RootErrorBoundary } from '@/app/errors/root-error-boundary';
import { PublicLayout } from '@/app/layouts/public-layout';
import { HomePage } from '@/pages/public/home-page';

export const router = createBrowserRouter([
    {
        ErrorBoundary: RootErrorBoundary,
        children: [
            {
                path: '/',
                Component: PublicLayout,
                children: [
                    {
                        index: true,
                        Component: HomePage,
                    },
                ],
            },
        ],
    },
]);
