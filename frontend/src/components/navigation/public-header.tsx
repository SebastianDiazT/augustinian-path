import { Link } from 'react-router';

import { BrandLogo } from '@/components/brand/brand-logo';
import { ThemeMenu } from '@/theme/theme-menu';

export function PublicHeader() {
    return (
        <header className='sticky top-0 z-50 h-20 border-b border-border bg-background/95 backdrop-blur-xl'>
            <div className='mx-auto flex h-full w-full max-w-7xl items-center justify-between gap-6 px-4 sm:px-6'>
                <Link
                    to='/'
                    className='inline-flex min-w-0 rounded-xl focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-primary'
                    aria-label='Ir al inicio de Ruta Agustina'
                >
                    <BrandLogo showTagline={false} />
                </Link>

                <ThemeMenu />
            </div>
        </header>
    );
}
