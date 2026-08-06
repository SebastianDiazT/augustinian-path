export const publicPaths = {
    home: '/',
    privacy: '/privacy',
    terms: '/terms',
    cookies: '/cookies',
    support: '/support',
    supportContact: '/support#contact',
} as const;

export const authPaths = {
    callback: '/auth/callback',
} as const;

export const studentPaths = {
    home: '/app',
} as const;

export const adminPaths = {
    home: '/admin',
    faculties: '/admin/faculties',
    professionalSchools: '/admin/professional-schools',
    curriculumPlans: '/admin/curriculum-plans',
    courses: '/admin/courses',
    curriculumCourses: '/admin/curriculum-courses',
    users: '/admin/users',
} as const;
