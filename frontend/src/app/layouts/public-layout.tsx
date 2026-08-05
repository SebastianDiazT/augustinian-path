import { Outlet } from 'react-router';

import { PublicFooter } from '@/components/layout/public-footer';
import { PublicHeader } from '@/components/navigation/public-header';

export function PublicLayout() {
    return (
        <div className='flex min-h-screen flex-col bg-background text-foreground transition-colors'>
            <PublicHeader />

            <main className='mx-auto w-full max-w-6xl flex-1 px-6 py-10'>
                <Outlet />
            </main>

            <PublicFooter />
        </div>
    );
}
