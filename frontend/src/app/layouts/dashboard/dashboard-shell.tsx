import { useEffect, useState } from 'react';
import type { PropsWithChildren } from 'react';

import type { CurrentUser } from '@/api/auth';
import { DashboardHeader } from '@/app/layouts/dashboard/dashboard-header';
import { DashboardSidebar } from '@/app/layouts/dashboard/dashboard-sidebar';
import type { DashboardNavigationGroup } from '@/app/layouts/dashboard/dashboard.types';

const SIDEBAR_STORAGE_KEY = 'ruta-agustina-sidebar-collapsed';

interface DashboardShellProps extends PropsWithChildren {
    areaLabel: string;
    navigation: DashboardNavigationGroup[];
    pageTitle: string;
    user: CurrentUser;
}

function getInitialSidebarState(): boolean {
    try {
        return window.localStorage.getItem(SIDEBAR_STORAGE_KEY) === 'true';
    } catch {
        return false;
    }
}

export function DashboardShell({
    areaLabel,
    children,
    navigation,
    pageTitle,
    user,
}: DashboardShellProps) {
    const [isCollapsed, setIsCollapsed] = useState(getInitialSidebarState);
    const [isMobileOpen, setIsMobileOpen] = useState(false);

    useEffect(() => {
        try {
            window.localStorage.setItem(SIDEBAR_STORAGE_KEY, String(isCollapsed));
        } catch {
            // El layout sigue funcionando si localStorage no está disponible.
        }
    }, [isCollapsed]);

    useEffect(() => {
        if (!isMobileOpen) {
            return;
        }

        const previousOverflow = document.body.style.overflow;

        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                setIsMobileOpen(false);
            }
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
            <a
                href='#dashboard-content'
                className='fixed left-4 top-4 z-70 -translate-y-24 rounded-xl bg-primary px-4 py-3 text-sm font-bold text-primary-foreground transition focus:translate-y-0'
            >
                Saltar al contenido
            </a>

            <DashboardSidebar
                className='fixed inset-y-0 left-0 z-40 hidden h-dvh lg:flex'
                collapsed={isCollapsed}
                navigation={navigation}
                onCollapse={() => setIsCollapsed((current) => !current)}
            />

            <div
                className={[
                    'fixed inset-0 z-50 transition lg:hidden',
                    isMobileOpen ? 'pointer-events-auto' : 'pointer-events-none',
                ].join(' ')}
                aria-hidden={!isMobileOpen}
            >
                <button
                    type='button'
                    className={[
                        'absolute inset-0 bg-black/45 backdrop-blur-[2px]',
                        'transition-opacity duration-200',
                        isMobileOpen ? 'opacity-100' : 'opacity-0',
                    ].join(' ')}
                    tabIndex={isMobileOpen ? 0 : -1}
                    aria-label='Cerrar navegación'
                    onClick={() => setIsMobileOpen(false)}
                />

                <div
                    className={[
                        'absolute inset-y-0 left-0 transition-transform',
                        'duration-200 ease-out',
                        isMobileOpen ? 'translate-x-0' : '-translate-x-full',
                    ].join(' ')}
                    inert={!isMobileOpen}
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

            <div
                className={[
                    'flex min-h-dvh min-w-0 flex-col',
                    'transition-[margin-left] duration-200 ease-out',
                    isCollapsed ? 'lg:ml-21' : 'lg:ml-72',
                ].join(' ')}
            >
                <DashboardHeader
                    areaLabel={areaLabel}
                    pageTitle={pageTitle}
                    user={user}
                    onOpenNavigation={() => setIsMobileOpen(true)}
                />

                <main
                    id='dashboard-content'
                    className='mx-auto w-full max-w-360 flex-1 px-4 py-6 sm:px-6 sm:py-8'
                    tabIndex={-1}
                >
                    {children}
                </main>
            </div>
        </div>
    );
}
