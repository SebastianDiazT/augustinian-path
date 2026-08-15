import { Outlet } from 'react-router-dom';
import { PublicHeader } from '@/components/navigation/public-header';
import { PublicFooter } from '@/components/layout/public-footer';

export default function PublicLayout() {
    return (
        <div className='flex min-h-screen flex-col bg-background text-foreground transition-colors'>
            <PublicHeader />

            <main className='flex-1'>
                <Outlet />
            </main>

            <PublicFooter />
        </div>
    );
}
