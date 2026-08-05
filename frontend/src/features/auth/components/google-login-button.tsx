import { useState } from 'react';

import { startGoogleLogin } from '@/features/auth/start-google-login';

export function GoogleLoginButton() {
    const [isRedirecting, setIsRedirecting] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function handleLogin(): Promise<void> {
        setIsRedirecting(true);
        setError(null);

        try {
            await startGoogleLogin();
        } catch {
            setIsRedirecting(false);
            setError('No se pudo iniciar el acceso con Google.');
        }
    }

    return (
        <div className='mt-6'>
            <button
                type='button'
                className='inline-flex min-h-11 w-full items-center justify-center rounded-xl bg-primary px-5 py-3 text-sm font-bold text-primary-foreground transition hover:bg-primary/90 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-wait disabled:opacity-70 sm:w-auto'
                disabled={isRedirecting}
                aria-busy={isRedirecting}
                aria-describedby={error ? 'google-login-error' : undefined}
                onClick={() => void handleLogin()}
            >
                {isRedirecting ? 'Redirigiendo a Google…' : 'Continuar con Google'}
            </button>

            {error ? (
                <p
                    id='google-login-error'
                    className='mt-3 text-sm font-semibold text-primary'
                    role='alert'
                >
                    {error}
                </p>
            ) : null}
        </div>
    );
}
