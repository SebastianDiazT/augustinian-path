import { Menu } from 'lucide-react';

import type { CurrentUser } from '@/api/auth';
import { UserMenu } from '@/app/layouts/dashboard/user-menu';
import type { DashboardPanel } from '@/app/layouts/dashboard/dashboard.types';
import { ThemeMenu } from '@/theme/theme-menu';

interface DashboardHeaderProps {
    activePanel: DashboardPanel;
    areaLabel: string;
    pageTitle: string;
    user: CurrentUser;
    onOpenNavigation: () => void;
}

export function DashboardHeader({
    activePanel,
    areaLabel,
    pageTitle,
    user,
    onOpenNavigation,
}: DashboardHeaderProps) {
    return (
        <header className='sticky top-0 z-30 flex min-h-20 items-center justify-between gap-4 border-b border-border bg-surface/95 px-4 shadow-sm backdrop-blur sm:px-6'>
            <div className='flex min-w-0 items-center gap-3'>
                <button
                    type='button'
                    className='inline-flex size-11 shrink-0 items-center justify-center rounded-xl text-muted-foreground transition hover:bg-surface-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-primary lg:hidden'
                    aria-label='Abrir navegación'
                    onClick={onOpenNavigation}
                >
                    <Menu className='size-5' aria-hidden='true' />
                </button>

                <div className='min-w-0'>
                    <p className='truncate text-[0.68rem] font-extrabold uppercase tracking-[0.16em] text-primary'>
                        {areaLabel}
                    </p>

                    <h1 className='truncate font-display text-lg font-extrabold tracking-tight sm:text-xl'>
                        {pageTitle}
                    </h1>
                </div>
            </div>

            <div className='flex shrink-0 items-center gap-1 sm:gap-2'>
                <ThemeMenu />
                <UserMenu activePanel={activePanel} user={user} />
            </div>
        </header>
    );
}
