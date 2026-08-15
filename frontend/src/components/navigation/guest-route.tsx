import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '@/store/auth-store';
import { privatePaths } from '@/app/paths';

export function GuestRoute() {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

    if (isAuthenticated) {
        return <Navigate to={privatePaths.dashboard} replace />;
    }

    return <Outlet />;
}
