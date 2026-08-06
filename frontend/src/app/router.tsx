import { createBrowserRouter } from 'react-router';

import { AdminRoute } from '@/app/guards/admin-route';
import { AdminLayout } from '@/app/layouts/admin-layout';
import { adminPaths } from '@/app/paths';
import { AdminHomePage } from '@/pages/admin/admin-home-page';
import { RootErrorBoundary } from '@/app/errors/root-error-boundary';
import { StudentRoute } from '@/app/guards/student-route';
import { PublicLayout } from '@/app/layouts/public-layout';
import { StudentLayout } from '@/app/layouts/student-layout';
import { authPaths, publicPaths, studentPaths } from '@/app/paths';
import { AuthCallbackPage } from '@/pages/auth/auth-callback-page';
import { CookiesPage } from '@/pages/public/cookies-page';
import { HomePage } from '@/pages/public/home-page';
import { PrivacyPage } from '@/pages/public/privacy-page';
import { SupportPage } from '@/pages/public/support-page';
import { TermsPage } from '@/pages/public/terms-page';
import { StudentHomePage } from '@/pages/student/student-home-page';

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
            {
                path: authPaths.callback,
                Component: AuthCallbackPage,
            },
            {
                Component: StudentRoute,
                children: [
                    {
                        path: studentPaths.home,
                        Component: StudentLayout,
                        children: [
                            {
                                index: true,
                                Component: StudentHomePage,
                            },
                        ],
                    },
                ],
            },
            {
                Component: AdminRoute,
                children: [
                    {
                        path: adminPaths.home,
                        Component: AdminLayout,
                        children: [
                            {
                                index: true,
                                Component: AdminHomePage,
                            },
                        ],
                    },
                ],
            },
        ],
    },
]);
