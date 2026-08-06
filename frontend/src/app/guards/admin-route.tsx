import { Link, Navigate, Outlet } from 'react-router';

import { publicPaths, studentPaths } from '@/app/paths';
import { AuthStateScreen } from '@/features/auth/components/auth-state-screen';
import { useCurrentUser } from '@/features/auth/use-current-user';

export function AdminRoute() {
    const session = useCurrentUser();

    if (session.status === 'pending') {
        return (
            <AuthStateScreen
                title='Abriendo la administración'
                description='Estamos comprobando tus permisos administrativos.'
            />
        );
    }

    if (session.status === 'error') {
        return (
            <AuthStateScreen
                title='No pudimos abrir la administración'
                description='El servidor no respondió correctamente. Comprueba tu conexión e inténtalo nuevamente.'
                tone='error'
            >
                <button
                    type='button'
                    className='min-h-11 rounded-xl bg-primary px-5 text-sm font-extrabold text-primary-foreground transition hover:bg-primary-hover'
                    onClick={() => void session.refetch()}
                >
                    Volver a intentar
                </button>
            </AuthStateScreen>
        );
    }

    if (session.data === null) {
        return <Navigate to={publicPaths.home} replace />;
    }

    if (!session.data.roles.includes('platform_admin')) {
        return (
            <AuthStateScreen
                title='Acceso administrativo no disponible'
                description='Tu cuenta no tiene asignado el rol necesario para entrar en este panel.'
                tone='error'
            >
                {session.data.roles.includes('student') ? (
                    <Link
                        to={studentPaths.home}
                        className='inline-flex min-h-11 items-center justify-center rounded-xl bg-primary px-5 text-sm font-extrabold text-primary-foreground transition hover:bg-primary-hover'
                    >
                        Ir al panel estudiantil
                    </Link>
                ) : null}
            </AuthStateScreen>
        );
    }

    return <Outlet context={session.data} />;
}
