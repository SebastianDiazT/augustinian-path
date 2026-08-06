import { NavLink } from 'react-router';

import type { DashboardNavigationGroup } from '@/app/layouts/dashboard/dashboard.types';

interface SidebarNavigationProps {
    collapsed: boolean;
    groups: DashboardNavigationGroup[];
    onNavigate?: () => void;
}

export function SidebarNavigation({
    collapsed,
    groups,
    onNavigate,
}: SidebarNavigationProps) {
    return (
        <nav
            className='flex flex-1 flex-col gap-6 overflow-y-auto px-3 py-5'
            aria-label='Navegación del panel'
        >
            {groups.map((group) => (
                <div key={group.label}>
                    {collapsed ? (
                        <div className='mx-3 mb-3 h-px bg-border' aria-hidden='true' />
                    ) : (
                        <p className='mb-2 px-3 text-[0.68rem] font-extrabold uppercase tracking-[0.16em] text-muted-foreground'>
                            {group.label}
                        </p>
                    )}

                    <div className='flex flex-col gap-1'>
                        {group.items.map((item) => {
                            const Icon = item.icon;

                            if (item.disabled) {
                                return (
                                    <div
                                        key={item.to}
                                        className={[
                                            'flex min-h-11 cursor-not-allowed',
                                            'items-center rounded-xl text-sm',
                                            'font-bold text-muted-foreground/55',
                                            collapsed
                                                ? 'justify-center px-2'
                                                : 'gap-3 px-3',
                                        ].join(' ')}
                                        aria-disabled='true'
                                        title={
                                            collapsed
                                                ? `${item.label} — próximamente`
                                                : undefined
                                        }
                                    >
                                        <Icon
                                            className='size-5 shrink-0'
                                            strokeWidth={2}
                                            aria-hidden='true'
                                        />

                                        {!collapsed ? (
                                            <>
                                                <span className='min-w-0 flex-1 truncate'>
                                                    {item.label}
                                                </span>

                                                <span className='text-[0.6rem] font-extrabold uppercase tracking-wider'>
                                                    Pronto
                                                </span>
                                            </>
                                        ) : null}
                                    </div>
                                );
                            }

                            return (
                                <NavLink
                                    key={item.to}
                                    to={item.to}
                                    end={item.end}
                                    title={collapsed ? item.label : undefined}
                                    aria-label={collapsed ? item.label : undefined}
                                    onClick={onNavigate}
                                    className={({ isActive }) =>
                                        [
                                            'group relative flex min-h-11 items-center rounded-xl',
                                            'text-sm font-bold transition-[background-color,color,box-shadow]',
                                            'focus-visible:outline-2 focus-visible:outline-offset-2',
                                            'focus-visible:outline-primary',
                                            collapsed
                                                ? 'justify-center px-2'
                                                : 'gap-3 px-3',
                                            isActive
                                                ? [
                                                      'bg-primary/10 text-primary shadow-sm',
                                                      'after:absolute after:inset-y-2',
                                                      'after:left-0 after:w-0.75',
                                                      'after:rounded-r-full after:bg-accent',
                                                  ].join(' ')
                                                : [
                                                      'text-muted-foreground',
                                                      'hover:bg-surface-muted',
                                                      'hover:text-foreground',
                                                  ].join(' '),
                                        ].join(' ')
                                    }
                                >
                                    <Icon
                                        className='size-5 shrink-0'
                                        strokeWidth={2}
                                        aria-hidden='true'
                                    />

                                    {!collapsed ? (
                                        <span className='truncate'>{item.label}</span>
                                    ) : null}
                                </NavLink>
                            );
                        })}
                    </div>
                </div>
            ))}
        </nav>
    );
}
