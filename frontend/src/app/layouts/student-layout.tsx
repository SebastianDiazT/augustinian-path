import { LayoutDashboard } from 'lucide-react';
import { Outlet, useOutletContext } from 'react-router';

import type { CurrentUser } from '@/api/auth';
import { DashboardShell } from '@/app/layouts/dashboard/dashboard-shell';
import type { DashboardNavigationGroup } from '@/app/layouts/dashboard/dashboard.types';
import { studentPaths } from '@/app/paths';

const studentNavigation: DashboardNavigationGroup[] = [
    {
        label: 'Principal',
        items: [
            {
                end: true,
                icon: LayoutDashboard,
                label: 'Resumen',
                to: studentPaths.home,
            },
        ],
    },
];

export function StudentLayout() {
    const user = useOutletContext<CurrentUser>();

    return (
        <DashboardShell
            areaLabel='Área estudiantil'
            navigation={studentNavigation}
            pageTitle='Resumen académico'
            user={user}
        >
            <Outlet context={user} />
        </DashboardShell>
    );
}
