import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/auth-store';
import { authPaths, privatePaths } from '@/app/paths';

export function GuestRoute() {
    const { user } = useAuthStore();
    const hasSession = Boolean(user);

    if (hasSession && user) {
        const hasCui = Boolean(user.cui);
        const hasMemberships = user.school_memberships && user.school_memberships.length > 0;

        if (!hasCui) {
            return <Navigate to={authPaths.onboardingCui} replace />;
        }

        if (hasCui && !hasMemberships) {
            return <Navigate to={authPaths.onboardingSchool} replace />;
        }

        return <Navigate to={privatePaths.dashboard} replace />;
    }

    return <Outlet />;
}
