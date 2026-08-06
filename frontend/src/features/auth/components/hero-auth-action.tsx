import { CheckCircle2, LoaderCircle } from 'lucide-react';

import { GoogleLoginButton } from '@/features/auth/components/google-login-button';
import { LogoutButton } from '@/features/auth/components/logout-button';
import { useCurrentUser } from '@/features/auth/use-current-user';

export function HeroAuthAction() {
    const session = useCurrentUser();

    if (session.status === 'pending') {
        return (
            <button
                type='button'
                className='inline-flex min-h-12 w-full cursor-wait items-center justify-center gap-2 rounded-xl bg-primary px-6 text-sm font-extrabold text-primary-foreground opacity-75 sm:w-auto'
                disabled
                aria-busy='true'
            >
                <LoaderCircle
                    className='size-4 motion-safe:animate-spin'
                    aria-hidden='true'
                />
                Comprobando sesión…
            </button>
        );
    }

    if (session.status === 'error') {
        return (
            <div>
                <GoogleLoginButton />

                <p className='mt-2 max-w-sm text-xs leading-5 text-muted-foreground'>
                    No pudimos comprobar tu sesión actual, pero puedes intentar
                    continuar con Google.
                </p>
            </div>
        );
    }

    if (session.data === null) {
        return <GoogleLoginButton />;
    }

    const greeting = session.data.first_name
        ? `Hola, ${session.data.first_name}`
        : 'Sesión iniciada';

    return (
        <div className='flex flex-col gap-2 sm:items-start'>
            <span className='inline-flex min-h-11 items-center gap-2 rounded-xl border border-emerald-500/25 bg-emerald-500/10 px-4 py-2.5 text-sm font-bold text-emerald-700 dark:text-emerald-300'>
                <CheckCircle2 className='size-4' aria-hidden='true' />
                {greeting}
            </span>

            <LogoutButton />
        </div>
    );
}
