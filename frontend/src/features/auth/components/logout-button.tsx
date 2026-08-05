import { useLogout } from '@/features/auth/use-logout';

export function LogoutButton() {
    const logout = useLogout();

    return (
        <div className='mt-6'>
            <button
                type='button'
                className='inline-flex min-h-11 items-center justify-center rounded-xl border border-border bg-surface px-5 py-3 text-sm font-bold text-foreground transition hover:bg-surface-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary disabled:cursor-wait disabled:opacity-70'
                disabled={logout.isPending}
                aria-busy={logout.isPending}
                aria-describedby={logout.isError ? 'logout-error' : undefined}
                onClick={() => logout.mutate()}
            >
                {logout.isPending ? 'Cerrando sesión…' : 'Cerrar sesión'}
            </button>

            {logout.isError ? (
                <p
                    id='logout-error'
                    className='mt-3 text-sm font-semibold text-primary'
                    role='alert'
                >
                    No se pudo cerrar la sesión.
                </p>
            ) : null}
        </div>
    );
}
