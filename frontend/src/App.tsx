import { ThemeSelector } from './theme/theme-selector';

import { SessionStatus } from './features/auth/components/session-status';

function App() {
    return (
        <main className='min-h-screen bg-background px-6 py-10 text-foreground transition-colors'>
            <div className='mx-auto max-w-5xl'>
                <SessionStatus />
                <header className='flex flex-wrap items-center justify-between gap-6'>
                    <div>
                        <p className='mb-2 text-xs font-bold uppercase tracking-[0.16em] text-primary'>
                            Universidad Nacional de San Agustín
                        </p>
                        <h1 className='font-display text-4xl font-extrabold tracking-[-0.045em] sm:text-5xl'>
                            Ruta UNSA
                        </h1>
                    </div>

                    <ThemeSelector />
                </header>

                <section className='mt-12 rounded-3xl border border-border bg-surface p-8 shadow-card sm:p-10'>
                    <span className='inline-flex rounded-full bg-accent px-3 py-1 text-sm font-semibold text-accent-foreground'>
                        Sistema visual
                    </span>

                    <h2 className='mt-5 font-display text-2xl font-bold tracking-[-0.025em]'>
                        Planifica tu camino. Construye tu futuro.
                    </h2>

                    <p className='mt-3 max-w-2xl text-[0.95rem] leading-7 font-medium text-muted-foreground'>
                        Esta pantalla verifica los colores semánticos y el cambio entre
                        los temas claro, oscuro y del sistema.
                    </p>

                    <div className='mt-8 grid gap-4 sm:grid-cols-3'>
                        <div className='rounded-2xl bg-primary p-5 text-primary-foreground'>
                            Acción principal
                        </div>
                        <div className='rounded-2xl bg-accent p-5 text-accent-foreground'>
                            Acento dorado
                        </div>
                        <div className='rounded-2xl border border-border bg-surface-muted p-5'>
                            Superficie secundaria
                        </div>
                    </div>
                </section>
                
            </div>
        </main>
    );
}

export default App;
