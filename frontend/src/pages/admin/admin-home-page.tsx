import { ShieldCheck } from 'lucide-react';
import { useOutletContext } from 'react-router';

import type { CurrentUser } from '@/api/auth';

export function AdminHomePage() {
    const user = useOutletContext<CurrentUser>();

    const displayName =
        [user.first_name, user.last_name].filter(Boolean).join(' ') || user.email;

    return (
        <section>
            <div className='rounded-3xl border border-border bg-surface p-7 shadow-card sm:p-9'>
                <span className='inline-flex size-12 items-center justify-center rounded-2xl bg-primary/10 text-primary'>
                    <ShieldCheck className='size-6' aria-hidden='true' />
                </span>

                <p className='mt-6 text-xs font-extrabold uppercase tracking-[0.16em] text-primary'>
                    Administración
                </p>

                <h2 className='mt-2 font-display text-3xl font-extrabold tracking-[-0.04em] sm:text-4xl'>
                    Bienvenido, {displayName}
                </h2>

                <p className='mt-4 max-w-2xl leading-7 text-muted-foreground'>
                    Desde este panel podrás gestionar la estructura académica y los
                    usuarios de Ruta Agustina. Los módulos se habilitarán a medida que
                    construyamos sus interfaces.
                </p>
            </div>
        </section>
    );
}
