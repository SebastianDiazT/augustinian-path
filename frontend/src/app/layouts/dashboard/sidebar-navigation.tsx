import { NavLink } from 'react-router-dom';
import type { DashboardNavigationGroup } from './dashboard.types';

interface SidebarNavigationProps {
    collapsed: boolean;
    groups: DashboardNavigationGroup[];
    onNavigate?: () => void;
}

export function SidebarNavigation({ collapsed, groups, onNavigate }: SidebarNavigationProps) {
    return (
        <nav className='flex-1 space-y-6 overflow-y-auto p-3 custom-scrollbar overflow-x-hidden'>
            {groups.map((group, groupIdx) => (
                <div key={groupIdx} className='space-y-1'>
                    {!collapsed && group.label && (
                        <p className='px-4 pb-2 text-xs font-bold uppercase tracking-wider text-muted-foreground/70'>
                            {group.label}
                        </p>
                    )}
                    {group.items.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            onClick={onNavigate}
                            title={collapsed ? item.label : undefined}
                            className={({ isActive }) =>
                                [
                                    'group flex items-center rounded-xl transition-all duration-200',
                                    collapsed
                                        ? 'justify-center p-3 mx-auto size-12'
                                        : 'px-4 py-3 gap-3',
                                    isActive
                                        ? 'bg-primary/10 text-primary font-semibold'
                                        : 'text-muted-foreground hover:bg-muted hover:text-foreground font-medium',
                                ].join(' ')
                            }
                        >
                            <item.icon
                                className={collapsed ? 'size-6 shrink-0' : 'size-5 shrink-0'}
                            />
                            <span
                                className={`overflow-hidden whitespace-nowrap transition-all duration-300 ${collapsed ? 'w-0 opacity-0' : 'w-auto opacity-100'}`}
                            >
                                {item.label}
                            </span>
                        </NavLink>
                    ))}
                </div>
            ))}
        </nav>
    );
}
