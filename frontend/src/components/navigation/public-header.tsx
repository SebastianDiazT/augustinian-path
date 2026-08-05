import { House, LogIn } from 'lucide-react';
import { BrandLogo } from '@/components/brand/brand-logo';
import { Link } from 'react-router';

import { ThemeSelector } from '@/theme/theme-selector';

export function PublicHeader() {
    return (
        <header className='sticky top-0 z-40 border-b border-border bg-surface/90 shadow-sm backdrop-blur-xl'>
            <div className='mx-auto flex min-h-18 w-full max-w-6xl items-center justify-between gap-4 px-4 sm:px-6'>
                <Link
                    to='/'
                    className='inline-flex min-w-0 items-center gap-3 rounded-xl focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary'
                    aria-label='Ir al inicio de Ruta Agustina'
                >
                    <BrandLogo />
                </Link>

                <nav
                    className='flex items-center gap-2'
                    aria-label='Navegación principal'
                >
                    <Link
                        to='/'
                        className='hidden min-h-10 items-center gap-2 rounded-xl px-3 text-sm font-semibold text-muted-foreground transition hover:bg-surface-muted hover:text-foreground md:inline-flex'
                    >
                        <House className='size-4' aria-hidden='true' />
                        Inicio
                    </Link>

                    <ThemeSelector />

                    <a
                        href='#access'
                        className='inline-flex min-h-10 items-center justify-center gap-2 rounded-xl bg-primary px-3 text-sm font-bold text-primary-foreground shadow-md shadow-primary/20 transition hover:-translate-y-0.5 hover:shadow-lg focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary sm:px-4'
                    >
                        <LogIn className='size-4' aria-hidden='true' />

                        <span className='hidden sm:inline'>Acceder</span>
                    </a>
                </nav>
            </div>
        </header>
    );
}
