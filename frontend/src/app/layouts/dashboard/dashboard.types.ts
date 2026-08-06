import type { LucideIcon } from 'lucide-react';

export type DashboardPanel = 'student' | 'admin';

export interface DashboardNavigationItem {
    disabled?: boolean;
    end?: boolean;
    icon: LucideIcon;
    label: string;
    to: string;
}

export interface DashboardNavigationGroup {
    items: DashboardNavigationItem[];
    label: string;
}
