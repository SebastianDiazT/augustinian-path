import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import PublicLayout from './layouts/public-layout';
import { PageLoader } from '@/components/ui/page-loader';
import { GuestRoute } from '@/components/navigation/guest-route';
import { AuthRoute } from '@/components/navigation/auth-route';

const HomePage = lazy(() => import('@/pages/public/home-page'));
const LoginPage = lazy(() => import('@/pages/auth/login-page'));
const OnboardingCuiPage = lazy(() => import('@/pages/auth/onboarding-cui-page'));
const OnboardingSchoolPage = lazy(() => import('@/pages/auth/onboarding-school-page'));
const PrivacyPage = lazy(() => import('@/pages/public/privacy-page'));
const TermsPage = lazy(() => import('@/pages/public/terms-page'));
const SupportPage = lazy(() => import('@/pages/public/support-page'));

const StudentLayout = lazy(() => import('@/app/layouts/student-layout'));

const DashboardPage = lazy(() => import('@/pages/private/student/dashboard-page'));

const NotFoundPage = lazy(() => import('@/pages/error/not-found-page'));
const ForbiddenPage = lazy(() => import('@/pages/error/forbidden-page'));

export function AppRouter() {
    return (
        <Suspense fallback={<PageLoader />}>
            <Routes>
                <Route element={<PublicLayout />}>
                    <Route path='/' element={<HomePage />} />
                    <Route path='/privacy' element={<PrivacyPage />} />
                    <Route path='/terms' element={<TermsPage />} />
                    <Route path='/support' element={<SupportPage />} />
                </Route>

                <Route element={<GuestRoute />}>
                    <Route path='/login' element={<LoginPage />} />
                </Route>

                <Route element={<AuthRoute />}>
                    <Route path='/onboarding/cui' element={<OnboardingCuiPage />} />
                    <Route path='/onboarding/school' element={<OnboardingSchoolPage />} />

                    <Route element={<StudentLayout />}>
                        <Route path='/student/dashboard' element={<DashboardPage />} />
                    </Route>
                </Route>

                <Route path='/403' element={<ForbiddenPage />} />

                <Route path='*' element={<NotFoundPage />} />
            </Routes>
        </Suspense>
    );
}
