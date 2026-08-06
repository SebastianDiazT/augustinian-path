import { Navigate, Outlet } from 'react-router';

import { publicPaths } from '@/app/paths';
import { AuthStateScreen } from '@/features/auth/components/auth-state-screen';
import { useCurrentUser } from '@/features/auth/use-current-user';

export function StudentRoute() {
    const session = useCurrentUser();

    if (session.status === 'pending') {
        return (
            <AuthStateScreen
                title='Abriendo tu panel'
                description='Estamos comprobando que tu sesión continúe activa.'
            />
        );
    }

    if (session.status === 'error') {
        return (
            <AuthStateScreen
                title='No pudimos abrir tu panel'
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

    if (!session.data.roles.includes('student')) {
        return (
            <AuthStateScreen
                title='Acceso estudiantil no disponible'
                description='Tu cuenta no tiene asignado el rol requerido para entrar en este panel.'
                tone='error'
            />
        );
    }

    return <Outlet context={session.data} />;
}
