import { CircleHelp, PanelLeftClose, PanelLeftOpen, X } from 'lucide-react';
import { Link } from 'react-router';

import type { DashboardNavigationGroup } from '@/app/layouts/dashboard/dashboard.types';
import { publicPaths } from '@/app/paths';
import { BrandLogo } from '@/components/brand/brand-logo';
import { BrandMark } from '@/components/brand/brand-mark';
import { SidebarNavigation } from '@/components/navigation/sidebar-navigation';

interface DashboardSidebarProps {
    className?: string;
    collapsed: boolean;
    navigation: DashboardNavigationGroup[];
    onClose?: () => void;
    onCollapse?: () => void;
    onNavigate?: () => void;
}

export function DashboardSidebar({
    className = '',
    collapsed,
    navigation,
    onClose,
    onCollapse,
    onNavigate,
}: DashboardSidebarProps) {
    return (
        <aside
            className={[
                'flex h-full shrink-0 flex-col border-r border-border',
                'bg-surface transition-[width] duration-200',
                collapsed ? 'w-21' : 'w-72',
                className,
            ].join(' ')}
        >
            <div
                className={[
                    'flex h-20 shrink-0 items-center border-b border-border',
                    collapsed ? 'justify-center px-3' : 'justify-between px-5',
                ].join(' ')}
            >
                {collapsed ? (
                    <BrandMark className='size-11' />
                ) : (
                    <BrandLogo showTagline={false} />
                )}

                {onClose ? (
                    <button
                        type='button'
                        className='inline-flex size-10 items-center justify-center rounded-xl text-muted-foreground transition hover:bg-surface-muted hover:text-foreground focus-visible:outline-2 focus-visible:outline-primary'
                        aria-label='Cerrar navegación'
                        onClick={onClose}
                    >
                        <X className='size-5' aria-hidden='true' />
                    </button>
                ) : null}
            </div>

            <SidebarNavigation
                collapsed={collapsed}
                groups={navigation}
                onNavigate={onNavigate}
            />

            <div className='border-t border-border p-3'>
                <Link
                    to={publicPaths.support}
                    title={collapsed ? 'Ayuda y soporte' : undefined}
                    className={[
                        'flex min-h-11 items-center rounded-xl text-sm font-bold',
                        'text-muted-foreground transition',
                        'hover:bg-surface-muted hover:text-foreground',
                        'focus-visible:outline-2 focus-visible:outline-primary',
                        collapsed ? 'justify-center px-2' : 'gap-3 px-3',
                    ].join(' ')}
                    onClick={onNavigate}
                >
                    <CircleHelp className='size-5 shrink-0' aria-hidden='true' />

                    {!collapsed ? <span>Ayuda y soporte</span> : null}
                </Link>

                {onCollapse ? (
                    <button
                        type='button'
                        className={[
                            'mt-1 flex min-h-11 w-full items-center rounded-xl',
                            'text-sm font-bold text-muted-foreground transition',
                            'hover:bg-surface-muted hover:text-foreground',
                            'focus-visible:outline-2 focus-visible:outline-primary',
                            collapsed ? 'justify-center px-2' : 'gap-3 px-3',
                        ].join(' ')}
                        title={
                            collapsed ? 'Expandir navegación' : 'Contraer navegación'
                        }
                        aria-label={
                            collapsed ? 'Expandir navegación' : 'Contraer navegación'
                        }
                        onClick={onCollapse}
                    >
                        {collapsed ? (
                            <PanelLeftOpen className='size-5' aria-hidden='true' />
                        ) : (
                            <>
                                <PanelLeftClose className='size-5' aria-hidden='true' />
                                <span>Contraer</span>
                            </>
                        )}
                    </button>
                ) : null}
            </div>
        </aside>
    );
}
