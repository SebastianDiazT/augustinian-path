import {
    BookOpen,
    Building2,
    GraduationCap,
    LayoutDashboard,
    Network,
    ScrollText,
    Users,
} from 'lucide-react';
import { Outlet, useOutletContext } from 'react-router';

import type { CurrentUser } from '@/api/auth';
import { DashboardShell } from '@/app/layouts/dashboard/dashboard-shell';
import type { DashboardNavigationGroup } from '@/app/layouts/dashboard/dashboard.types';
import { adminPaths } from '@/app/paths';

const adminNavigation: DashboardNavigationGroup[] = [
    {
        label: 'Principal',
        items: [
            {
                end: true,
                icon: LayoutDashboard,
                label: 'Resumen',
                to: adminPaths.home,
            },
        ],
    },
    {
        label: 'Gestión académica',
        items: [
            {
                disabled: true,
                icon: Building2,
                label: 'Facultades',
                to: adminPaths.faculties,
            },
            {
                disabled: true,
                icon: GraduationCap,
                label: 'Escuelas profesionales',
                to: adminPaths.professionalSchools,
            },
            {
                disabled: true,
                icon: ScrollText,
                label: 'Planes de estudio',
                to: adminPaths.curriculumPlans,
            },
            {
                disabled: true,
                icon: BookOpen,
                label: 'Cursos',
                to: adminPaths.courses,
            },
            {
                disabled: true,
                icon: Network,
                label: 'Malla curricular',
                to: adminPaths.curriculumCourses,
            },
        ],
    },
    {
        label: 'Administración',
        items: [
            {
                disabled: true,
                icon: Users,
                label: 'Usuarios',
                to: adminPaths.users,
            },
        ],
    },
];

export function AdminLayout() {
    const user = useOutletContext<CurrentUser>();

    return (
        <DashboardShell
            activePanel='admin'
            areaLabel='Administración'
            navigation={adminNavigation}
            pageTitle='Resumen general'
            user={user}
        >
            <Outlet context={user} />
        </DashboardShell>
    );
}
