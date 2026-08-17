import { LayoutDashboard, Map, CalendarDays } from 'lucide-react';
import { Outlet, useLocation } from 'react-router-dom';
import { DashboardShell } from '@/app/layouts/dashboard/dashboard-shell';
import type { DashboardNavigationGroup } from '@/app/layouts/dashboard/dashboard.types';
import { privatePaths } from '@/app/paths';

const studentNavigation: DashboardNavigationGroup[] = [
    {
        label: 'Académico',
        items: [
            { label: 'Mi Panel', to: privatePaths.dashboard, icon: LayoutDashboard },
            { label: 'Malla Curricular', to: '/student/curriculum', icon: Map },
            { label: 'Horarios', to: '/student/schedule', icon: CalendarDays },
        ],
    },
];

const pageTitles: Record<string, string> = {
    [privatePaths.dashboard]: 'Resumen General',
    '/student/curriculum': 'Malla Curricular',
    '/student/schedule': 'Simulador de Horarios',
};

export default function StudentLayout() {
    const location = useLocation();
    const currentPageTitle = pageTitles[location.pathname] || 'Panel Estudiantil';

    return (
        <DashboardShell
            activePanel='student'
            areaLabel='Ruta Agustina'
            pageTitle={currentPageTitle}
            navigation={studentNavigation}
        >
            <Outlet />
        </DashboardShell>
    );
}
