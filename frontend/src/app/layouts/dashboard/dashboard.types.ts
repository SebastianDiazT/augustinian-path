import type { LucideIcon } from 'lucide-react';

export interface DashboardNavigationItem {
    end?: boolean;
    icon: LucideIcon;
    label: string;
    to: string;
}

export interface DashboardNavigationGroup {
    items: DashboardNavigationItem[];
    label: string;
}
