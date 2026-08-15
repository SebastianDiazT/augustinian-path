import { Outlet } from 'react-router-dom';
import { ES_UI } from '@/locales/es';

export default function PublicLayout() {
    return (
        <div className='flex min-h-screen flex-col bg-background text-foreground transition-colors'>
            {/* Header Placeholder (Lo armaremos a detalle después) */}
            <header className='sticky top-0 z-50 flex h-16 items-center justify-between border-b border-border bg-background/95 px-6 backdrop-blur-xl'>
                <span className='font-display font-extrabold text-primary'>{ES_UI.brand.name}</span>
            </header>

            <main className='flex-1'>
                {/* Aquí adentro se inyectará la Landing Page */}
                <Outlet />
            </main>

            {/* Footer Placeholder */}
            <footer className='border-t border-border bg-muted/30 py-8 text-center text-sm text-muted-foreground'>
                {ES_UI.legal.copyright.replace('{year}', new Date().getFullYear().toString())}
            </footer>
        </div>
    );
}
