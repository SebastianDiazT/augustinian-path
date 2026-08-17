import { useEffect, useState } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuthStore } from '@/store/auth-store';
import { publicPaths, privatePaths } from '@/app/paths';
import { PageLoader } from '@/components/ui/page-loader';

export function AuthRoute() {
    const { isAuthenticated, user, syncProfile } = useAuthStore();
    const [isFetching, setIsFetching] = useState(!user);
    const location = useLocation();

    useEffect(() => {
        if (!isAuthenticated) return;

        syncProfile().finally(() => {
            setIsFetching(false);
        });
    }, [isAuthenticated, syncProfile]);

    if (!isAuthenticated) {
        return <Navigate to={publicPaths.login} state={{ from: location }} replace />;
    }

    if (isFetching || !user) {
        return <PageLoader />;
    }

    const hasCui = !!user.cui;
    const hasMembership = user.school_memberships && user.school_memberships.length > 0;

    const isAtCuiRoute = location.pathname === privatePaths.onboardingCui;
    const isAtSchoolRoute = location.pathname === privatePaths.onboardingSchool;

    if (!hasCui && !isAtCuiRoute) {
        return <Navigate to={privatePaths.onboardingCui} replace />;
    }

    if (hasCui && !hasMembership && !isAtSchoolRoute) {
        return <Navigate to={privatePaths.onboardingSchool} replace />;
    }

    if (hasCui && hasMembership && (isAtCuiRoute || isAtSchoolRoute)) {
        return <Navigate to={privatePaths.dashboard} replace />;
    }

    return <Outlet />;
}
