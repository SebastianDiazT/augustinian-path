import { createBrowserRouter } from 'react-router';

import { RootErrorBoundary } from '@/app/errors/root-error-boundary';
import { PublicLayout } from '@/app/layouts/public-layout';
import { publicPaths } from '@/app/paths';
import { CookiesPage } from '@/pages/public/cookies-page';
import { HomePage } from '@/pages/public/home-page';
import { PrivacyPage } from '@/pages/public/privacy-page';
import { SupportPage } from '@/pages/public/support-page';
import { TermsPage } from '@/pages/public/terms-page';

export const router = createBrowserRouter([
    {
        ErrorBoundary: RootErrorBoundary,
        children: [
            {
                path: publicPaths.home,
                Component: PublicLayout,
                children: [
                    {
                        index: true,
                        Component: HomePage,
                    },
                    {
                        path: publicPaths.privacy,
                        Component: PrivacyPage,
                    },
                    {
                        path: publicPaths.terms,
                        Component: TermsPage,
                    },
                    {
                        path: publicPaths.cookies,
                        Component: CookiesPage,
                    },
                    {
                        path: publicPaths.support,
                        Component: SupportPage,
                    },
                ],
            },
        ],
    },
]);
