import { CircleHelp, PanelLeftClose, PanelLeftOpen, X } from 'lucide-react';
import { Link } from 'react-router-dom';
import type { DashboardNavigationGroup } from './dashboard.types';
import { publicPaths } from '@/app/paths';
import { BrandLogo } from '@/components/brand/brand-logo';
import { BrandMark } from '@/components/brand/brand-mark';
import { SidebarNavigation } from './sidebar-navigation';

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
                'flex h-full shrink-0 flex-col border-r border-border bg-surface/80 backdrop-blur-xl transition-[width] duration-300 ease-in-out',
                collapsed ? 'w-20' : 'w-72',
                className,
            ].join(' ')}
        >
            <div
                className={[
                    'flex h-20 shrink-0 items-center border-b border-border transition-all duration-300 overflow-hidden',
                    collapsed ? 'justify-center px-0' : 'justify-between px-5',
                ].join(' ')}
            >
                {/* Aquí usamos tu nuevo Isotipo o el Logo completo */}
                {collapsed ? (
                    <BrandMark className='size-11 shrink-0' />
                ) : (
                    <BrandLogo showTagline={false} className='scale-90 shrink-0' />
                )}

                {onClose && !collapsed && (
                    <button
                        type='button'
                        className='inline-flex size-8 items-center justify-center rounded-lg text-muted-foreground transition hover:bg-muted focus:outline-none'
                        onClick={onClose}
                    >
                        <X className='size-5' />
                    </button>
                )}
            </div>

            {/* Componente extraído */}
            <SidebarNavigation collapsed={collapsed} groups={navigation} onNavigate={onNavigate} />

            <div className='border-t border-border p-3 space-y-1'>
                <Link
                    to={publicPaths.support}
                    title={collapsed ? 'Ayuda y soporte' : undefined}
                    onClick={onNavigate}
                    className={[
                        'flex items-center rounded-xl text-sm font-medium text-muted-foreground transition hover:bg-muted hover:text-foreground',
                        collapsed ? 'justify-center p-3 size-12 mx-auto' : 'px-4 py-3 gap-3',
                    ].join(' ')}
                >
                    <CircleHelp className='size-5 shrink-0' />
                    <span
                        className={`overflow-hidden whitespace-nowrap transition-all duration-300 ${collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'}`}
                    >
                        Soporte
                    </span>
                </Link>

                {onCollapse && (
                    <button
                        type='button'
                        onClick={onCollapse}
                        title={collapsed ? 'Expandir menú' : 'Minimizar menú'}
                        className={[
                            'flex w-full items-center rounded-xl text-sm font-medium text-muted-foreground transition hover:bg-muted hover:text-foreground',
                            collapsed ? 'justify-center p-3 size-12 mx-auto' : 'px-4 py-3 gap-3',
                        ].join(' ')}
                    >
                        {collapsed ? (
                            <PanelLeftOpen className='size-5 shrink-0' />
                        ) : (
                            <PanelLeftClose className='size-5 shrink-0' />
                        )}
                        <span
                            className={`overflow-hidden whitespace-nowrap transition-all duration-300 ${collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'}`}
                        >
                            Minimizar menú
                        </span>
                    </button>
                )}
            </div>
        </aside>
    );
}
