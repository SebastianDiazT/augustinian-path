import { useEffect, useState } from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import axios from 'axios';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/auth-store';
import { publicPaths, privatePaths } from '@/app/paths';
import { PageLoader } from '@/components/ui/page-loader';
import { type CurrentUser } from '@/types/auth';

export function AuthRoute() {
    const { isAuthenticated, user, setUser, clearAuth } = useAuthStore();
    const [isFetching, setIsFetching] = useState(!user);
    const location = useLocation();

    useEffect(() => {
        let mounted = true;

        const syncUser = async () => {
            if (!isAuthenticated) return;
            try {
                const res = await api.get('/accounts/users/me/');
                if (mounted) {
                    setUser(res.data as CurrentUser);
                }
            } catch (error: unknown) {
                console.error('Error al sincronizar el perfil:', error);
                if (mounted && axios.isAxiosError(error) && error.response?.status === 401) {
                    toast.error('Tu sesión ha expirado. Por favor, vuelve a iniciar sesión.');
                    clearAuth();
                }
            } finally {
                if (mounted) setIsFetching(false);
            }
        };

        syncUser();

        return () => {
            mounted = false;
        };
    }, [isAuthenticated, setUser, clearAuth]);

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
