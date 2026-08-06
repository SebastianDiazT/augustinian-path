import { Outlet, ScrollRestoration } from 'react-router';

import { PublicFooter } from '@/components/layout/public-footer';
import { PublicHeader } from '@/components/navigation/public-header';

export function PublicLayout() {
    return (
        <div className='flex min-h-screen flex-col bg-background text-foreground transition-colors'>
            <PublicHeader />

            <main className='flex-1'>
                <Outlet />
            </main>

            <PublicFooter />
            <ScrollRestoration />
        </div>
    );
}
