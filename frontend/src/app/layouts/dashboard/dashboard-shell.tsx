import { useEffect, useState } from 'react';
import type { PropsWithChildren } from 'react';
import { Menu } from 'lucide-react';
import type { DashboardNavigationGroup, DashboardPanel } from './dashboard.types';
import { DashboardSidebar } from './dashboard-sidebar';
import { UserMenu } from './user-menu';
import { ThemeMenu } from '@/theme/theme-menu';

const SIDEBAR_STORAGE_KEY = 'ruta-agustina-sidebar-collapsed';

interface DashboardShellProps extends PropsWithChildren {
    activePanel: DashboardPanel;
    areaLabel: string;
    navigation: DashboardNavigationGroup[];
    pageTitle: string;
}

export function DashboardShell({
    activePanel,
    areaLabel,
    children,
    navigation,
    pageTitle,
}: DashboardShellProps) {
    const [isCollapsed, setIsCollapsed] = useState(() => {
        try {
            return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === 'true';
        } catch {
            return false;
        }
    });

    const [isMobileOpen, setIsMobileOpen] = useState(false);

    useEffect(() => {
        try {
            window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isCollapsed));
        } catch {
            /* Ignorar si no hay localStorage */
        }
    }, [isCollapsed]);

    useEffect(() => {
        if (!isMobileOpen) return;
        const previousOverflow = document.body.style.overflow;
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') setIsMobileOpen(false);
        };
        document.body.style.overflow = 'hidden';
        document.addEventListener('keydown', handleKeyDown);
        return () => {
            document.body.style.overflow = previousOverflow;
            document.removeEventListener('keydown', handleKeyDown);
        };
    }, [isMobileOpen]);

    return (
        <div className='min-h-dvh bg-background text-foreground'>
            {/* SIDEBAR DESKTOP (FIJO Y ALTO COMPLETO) */}
            <DashboardSidebar
                className='fixed inset-y-0 left-0 z-40 hidden h-dvh lg:flex'
                collapsed={isCollapsed}
                navigation={navigation}
                onCollapse={() => setIsCollapsed(!isCollapsed)}
            />

            {/* SIDEBAR MÓVIL (Overlay) */}
            <div
                className={[
                    'fixed inset-0 z-50 transition-all lg:hidden',
                    isMobileOpen ? 'pointer-events-auto' : 'pointer-events-none',
                ].join(' ')}
            >
                <div
                    className={[
                        'absolute inset-0 bg-background/80 backdrop-blur-sm transition-opacity duration-300',
                        isMobileOpen ? 'opacity-100' : 'opacity-0',
                    ].join(' ')}
                    onClick={() => setIsMobileOpen(false)}
                />
                <div
                    className={[
                        'absolute inset-y-0 left-0 transition-transform duration-300 ease-out',
                        isMobileOpen ? 'translate-x-0' : '-translate-x-full',
                    ].join(' ')}
                >
                    <DashboardSidebar
                        className='h-dvh w-72 shadow-2xl'
                        collapsed={false}
                        navigation={navigation}
                        onClose={() => setIsMobileOpen(false)}
                        onNavigate={() => setIsMobileOpen(false)}
                    />
                </div>
            </div>

            {/* COLUMNA PRINCIPAL (CON MARGEN IZQUIERDO DINÁMICO) */}
            <div
                className={[
                    'flex min-h-dvh min-w-0 flex-col transition-[margin-left] duration-300 ease-in-out',
                    isCollapsed ? 'lg:ml-20' : 'lg:ml-72',
                ].join(' ')}
            >
                {/* HEADER */}
                <header className='sticky top-0 z-30 flex h-20 shrink-0 items-center justify-between gap-4 border-b border-border bg-surface/80 px-4 backdrop-blur-xl sm:px-6 lg:px-8'>
                    <div className='flex min-w-0 items-center gap-4'>
                        <button
                            type='button'
                            className='inline-flex size-10 shrink-0 items-center justify-center rounded-xl text-muted-foreground transition hover:bg-muted focus:outline-none lg:hidden'
                            onClick={() => setIsMobileOpen(true)}
                        >
                            <Menu className='size-6' />
                        </button>
                        <div className='min-w-0'>
                            <p className='truncate text-[0.65rem] font-extrabold uppercase tracking-widest text-primary'>
                                {areaLabel}
                            </p>
                            <h1 className='truncate font-display text-lg font-extrabold tracking-tight sm:text-2xl text-foreground'>
                                {pageTitle}
                            </h1>
                        </div>
                    </div>
                    <div className='flex shrink-0 items-center gap-2 sm:gap-4'>
                        <ThemeMenu />
                        <div className='h-8 w-px bg-border mx-1 hidden sm:block' />
                        <UserMenu activePanel={activePanel} />
                    </div>
                </header>

                {/* CONTENIDO (Outlet) */}
                <main className='flex-1 p-4 sm:p-6 lg:p-8'>
                    <div className='mx-auto w-full max-w-6xl'>{children}</div>
                </main>
            </div>
        </div>
    );
}
