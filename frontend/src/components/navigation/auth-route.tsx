import { Navigate, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/auth-store';
import { authPaths, privatePaths } from '@/app/paths';

export function AuthRoute() {
    const { user } = useAuthStore();
    const location = useLocation();

    const hasSession = Boolean(user);

    if (!hasSession || !user) {
        return <Navigate to={authPaths.login} state={{ from: location }} replace />;
    }

    const hasCui = Boolean(user.cui);
    const hasMemberships = user.school_memberships && user.school_memberships.length > 0;
    const currentPath = location.pathname;

    if (!hasCui) {
        if (currentPath !== authPaths.onboardingCui) {
            return <Navigate to={authPaths.onboardingCui} replace />;
        }
        return <Outlet />;
    }

    if (hasCui && !hasMemberships) {
        if (currentPath !== authPaths.onboardingSchool) {
            return <Navigate to={authPaths.onboardingSchool} replace />;
        }
        return <Outlet />;
    }

    if (hasCui && hasMemberships) {
        if (currentPath === authPaths.onboardingCui || currentPath === authPaths.onboardingSchool) {
            return <Navigate to={privatePaths.dashboard} replace />;
        }
        return <Outlet />;
    }

    return <Outlet />;
}
