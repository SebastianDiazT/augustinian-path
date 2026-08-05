import { CircleAlert, House, RefreshCw } from 'lucide-react';
import { isRouteErrorResponse, Link, useRouteError } from 'react-router';

export function RootErrorBoundary() {
    const error = useRouteError();

    const isNotFound = isRouteErrorResponse(error) && error.status === 404;

    const title = isNotFound ? 'Página no encontrada' : 'Algo salió mal';

    const description = isNotFound
        ? 'La dirección que ingresaste no existe o fue movida.'
        : 'No pudimos mostrar esta página. Intenta nuevamente.';

    return (
        <main className='flex min-h-screen items-center justify-center bg-background px-6 py-12 text-foreground'>
            <section className='w-full max-w-lg rounded-3xl border border-border bg-surface p-8 text-center shadow-card sm:p-10'>
                <span className='mx-auto inline-flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary dark:bg-primary/20'>
                    <CircleAlert className='size-7' aria-hidden='true' />
                </span>

                <p className='mt-6 text-xs font-bold uppercase tracking-[0.16em] text-primary'>
                    {isNotFound ? 'Error 404' : 'Error de aplicación'}
                </p>

                <h1 className='mt-3 font-display text-3xl font-extrabold tracking-[-0.04em]'>
                    {title}
                </h1>

                <p className='mt-3 leading-7 text-muted-foreground'>{description}</p>

                <div className='mt-8 flex flex-col justify-center gap-3 sm:flex-row'>
                    <Link
                        to='/'
                        className='inline-flex min-h-11 items-center justify-center gap-2 rounded-xl bg-primary px-5 py-3 text-sm font-bold text-primary-foreground'
                    >
                        <House className='size-4' aria-hidden='true' />
                        Volver al inicio
                    </Link>

                    {!isNotFound ? (
                        <button
                            type='button'
                            className='inline-flex min-h-11 items-center justify-center gap-2 rounded-xl border border-border bg-surface px-5 py-3 text-sm font-bold transition hover:bg-surface-muted'
                            onClick={() => window.location.reload()}
                        >
                            <RefreshCw className='size-4' aria-hidden='true' />
                            Reintentar
                        </button>
                    ) : null}
                </div>
            </section>
        </main>
    );
}
