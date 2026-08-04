import type { UserRole } from '../../../api/auth';
import { useCurrentUser } from '../use-current-user';

const containerClasses =
    'mt-6 rounded-3xl border border-border ' + 'bg-surface p-8 shadow-card sm:p-10';

const roleLabels: Record<UserRole, string> = {
    platform_admin: 'Administrador',
    student: 'Estudiante',
};

export function SessionStatus() {
    const session = useCurrentUser();

    if (session.status === 'pending') {
        return (
            <section className={containerClasses} aria-busy='true'>
                <p className='text-muted-foreground' role='status'>
                    Comprobando tu sesión…
                </p>
            </section>
        );
    }

    if (session.status === 'error') {
        return (
            <section className={containerClasses} role='alert'>
                <p className='font-bold text-primary'>
                    No se pudo conectar con el backend.
                </p>
                <p className='mt-2 text-muted-foreground'>
                    Comprueba que Django esté ejecutándose.
                </p>
            </section>
        );
    }

    if (session.data === null) {
        return (
            <section className={containerClasses}>
                <p className='text-xs font-bold uppercase tracking-[0.16em] text-primary'>
                    Acceso institucional
                </p>
                <h2 className='mt-3 font-display text-2xl font-bold tracking-[-0.025em]'>
                    Sesión no iniciada
                </h2>
                <p className='mt-3 text-muted-foreground'>
                    Inicia sesión con tu cuenta institucional de la UNSA para continuar.
                </p>
            </section>
        );
    }

    const user = session.data;

    return (
        <section className={containerClasses}>
            <p className='text-xs font-bold uppercase tracking-[0.16em] text-primary'>
                Sesión institucional
            </p>

            <h2 className='mt-3 font-display text-2xl font-bold tracking-[-0.025em]'>
                {user.first_name
                    ? `Bienvenido, ${user.first_name}`
                    : 'Bienvenido a Ruta UNSA'}
            </h2>

            <p className='mt-2 text-muted-foreground'>{user.email}</p>

            <div className='mt-5 flex flex-wrap gap-2'>
                {user.roles.length > 0 ? (
                    user.roles.map((role) => (
                        <span
                            key={role}
                            className='rounded-full bg-primary/10 px-3 py-1 text-sm font-semibold text-primary dark:bg-primary/20'
                        >
                            {roleLabels[role]}
                        </span>
                    ))
                ) : (
                    <span className='text-sm text-muted-foreground'>
                        Sin roles asignados
                    </span>
                )}
            </div>
        </section>
    );
}
