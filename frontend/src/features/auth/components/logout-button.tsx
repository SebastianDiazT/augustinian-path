import { LoaderCircle, LogOut } from 'lucide-react';
import { useId } from 'react';

import { useLogout } from '@/features/auth/use-logout';

interface LogoutButtonProps {
    className?: string;
}

export function LogoutButton({ className = '' }: LogoutButtonProps) {
    const logout = useLogout();
    const errorId = useId();

    return (
        <div className={className}>
            <button
                type='button'
                className='group inline-flex min-h-11 w-full items-center justify-center gap-2 rounded-xl border border-border bg-surface px-5 py-2.5 text-sm font-bold text-foreground transition-[transform,background-color,border-color] duration-200 hover:border-primary/25 hover:bg-surface-muted active:translate-y-px focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-wait disabled:opacity-70 sm:w-auto'
                disabled={logout.isPending}
                aria-busy={logout.isPending}
                aria-describedby={logout.isError ? errorId : undefined}
                onClick={() => logout.mutate()}
            >
                {logout.isPending ? (
                    <LoaderCircle
                        className='size-4 motion-safe:animate-spin'
                        aria-hidden='true'
                    />
                ) : (
                    <LogOut
                        className='size-4 transition-transform duration-200 motion-safe:group-hover:translate-x-0.5'
                        aria-hidden='true'
                    />
                )}

                {logout.isPending ? 'Cerrando sesión…' : 'Cerrar sesión'}
            </button>

            {logout.isError ? (
                <p
                    id={errorId}
                    className='mt-2 max-w-sm text-xs font-semibold text-primary'
                    role='alert'
                >
                    No se pudo cerrar la sesión.
                </p>
            ) : null}
        </div>
    );
}
