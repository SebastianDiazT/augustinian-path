import { LoaderCircle, LogIn } from 'lucide-react';
import { useId, useState } from 'react';

import { startGoogleLogin } from '@/features/auth/start-google-login';

interface GoogleLoginButtonProps {
    className?: string;
}

export function GoogleLoginButton({ className = '' }: GoogleLoginButtonProps) {
    const [isRedirecting, setIsRedirecting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const errorId = useId();

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
        <div className={className}>
            <button
                type='button'
                className='group inline-flex min-h-12 w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 text-sm font-extrabold text-primary-foreground shadow-md shadow-primary/20 transition-[transform,background-color,box-shadow] duration-200 hover:bg-primary-hover hover:shadow-lg active:translate-y-px focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-wait disabled:opacity-70 sm:w-auto'
                disabled={isRedirecting}
                aria-busy={isRedirecting}
                aria-describedby={error ? errorId : undefined}
                onClick={() => void handleLogin()}
            >
                {isRedirecting ? (
                    <LoaderCircle
                        className='size-4 motion-safe:animate-spin'
                        aria-hidden='true'
                    />
                ) : (
                    <LogIn
                        className='size-4 transition-transform duration-200 motion-safe:group-hover:translate-x-0.5'
                        aria-hidden='true'
                    />
                )}

                {isRedirecting ? 'Redirigiendo a Google…' : 'Continuar con Google'}
            </button>

            {error ? (
                <p
                    id={errorId}
                    className='mt-3 max-w-sm text-sm font-semibold text-primary'
                    role='alert'
                >
                    {error}
                </p>
            ) : null}
        </div>
    );
}
