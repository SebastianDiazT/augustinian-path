import { useOutletContext } from 'react-router';

import type { CurrentUser } from '@/api/auth';

export function StudentHomePage() {
    const user = useOutletContext<CurrentUser>();

    const displayName =
        [user.first_name, user.last_name].filter(Boolean).join(' ') || 'Estudiante';

    return (
        <main className='min-h-screen bg-background px-6 py-12 text-foreground'>
            <section className='mx-auto max-w-5xl rounded-3xl border border-border bg-surface p-8 shadow-card sm:p-10'>
                <p className='text-xs font-extrabold uppercase tracking-[0.16em] text-primary'>
                    Panel estudiantil
                </p>

                <h1 className='mt-3 font-display text-3xl font-extrabold tracking-[-0.04em] sm:text-4xl'>
                    Bienvenido, {displayName}
                </h1>

                <p className='mt-3 text-muted-foreground'>{user.email}</p>

                <p className='mt-8 max-w-2xl leading-7 text-muted-foreground'>
                    Tu sesión institucional está funcionando correctamente. El siguiente
                    paso será construir aquí el layout estudiantil con sidebar,
                    encabezado y navegación.
                </p>
            </section>
        </main>
    );
}
