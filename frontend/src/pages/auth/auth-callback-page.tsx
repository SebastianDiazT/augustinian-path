import { useEffect } from 'react';

import { Link, useNavigate } from 'react-router';

import { publicPaths, studentPaths } from '@/app/paths';
import { AuthStateScreen } from '@/features/auth/components/auth-state-screen';
import { GoogleLoginButton } from '@/features/auth/components/google-login-button';
import { useCurrentUser } from '@/features/auth/use-current-user';

export function AuthCallbackPage() {
    const navigate = useNavigate();
    const session = useCurrentUser();

    const canOpenStudentPanel = session.data?.roles.includes('student') ?? false;

    useEffect(() => {
        if (!canOpenStudentPanel) {
            return;
        }

        navigate(studentPaths.home, {
            replace: true,
        });
    }, [canOpenStudentPanel, navigate]);

    if (session.status === 'pending') {
        return (
            <AuthStateScreen
                title='Comprobando tu cuenta'
                description='Estamos verificando la sesión institucional creada con Google.'
            />
        );
    }

    if (session.status === 'error') {
        return (
            <AuthStateScreen
                title='No pudimos verificar tu sesión'
                description='Ocurrió un problema al comunicarnos con el servidor.'
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

    if (canOpenStudentPanel) {
        return (
            <AuthStateScreen
                title='Preparando tu panel'
                description='La autenticación se completó correctamente. Serás redirigido en un momento.'
            />
        );
    }

    if (session.data !== null) {
        return (
            <AuthStateScreen
                title='Tu cuenta no tiene acceso estudiantil'
                description='La sesión se inició correctamente, pero tu cuenta no tiene asignado el rol de estudiante.'
                tone='error'
            >
                <Link
                    to={publicPaths.home}
                    className='inline-flex min-h-11 items-center justify-center rounded-xl border border-border px-5 text-sm font-bold transition hover:bg-surface-muted'
                >
                    Volver al inicio
                </Link>
            </AuthStateScreen>
        );
    }

    return (
        <AuthStateScreen
            title='No se completó el inicio de sesión'
            description='Google no creó una sesión válida. Puedes volver a intentarlo.'
            tone='error'
        >
            <div className='flex flex-col gap-3 sm:flex-row'>
                <GoogleLoginButton />

                <Link
                    to={publicPaths.home}
                    className='inline-flex min-h-11 items-center justify-center rounded-xl border border-border px-5 text-sm font-bold transition hover:bg-surface-muted'
                >
                    Volver al inicio
                </Link>
            </div>
        </AuthStateScreen>
    );
}
