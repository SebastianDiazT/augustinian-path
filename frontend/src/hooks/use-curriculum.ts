import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { useAuthStore } from '@/store/auth-store';

export interface Course {
    public_id: string;
    curriculum_plan: string;
    code: string;
    name: string;
    credits: string;
    theory_hours: number;
    practice_hours: number;
    lab_hours: number;
    cycle: number;
    course_type: 'mandatory' | 'elective';
    academic_area: string;
    has_lab: boolean;
}
export interface Prerequisite {
    public_id: string;
    course: string;
    required_course: string;
}

export function useCurriculum() {
    const { user } = useAuthStore();
    const [courses, setCourses] = useState<Course[]>([]);
    const [prerequisites, setPrerequisites] = useState<Prerequisite[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const activeMembership = user?.school_memberships?.find((m) => m.is_active);
    const planId = activeMembership?.curriculum_plan;

    // 2. La función de carga vive dentro del efecto (The React Way)
    useEffect(() => {
        let mounted = true;

        const fetchCurriculumData = async () => {
            if (!planId) {
                if (mounted) setIsLoading(false);
                return;
            }

            try {
                // Pedimos cursos y prerrequisitos en paralelo
                const [coursesRes, prereqRes] = await Promise.all([
                    api.get(`/curricula/courses/?curriculum_plan=${planId}`),
                    api.get(`/curricula/prerequisites/`),
                ]);

                if (!mounted) return;

                const fetchedCourses: Course[] = coursesRes.data.data || coursesRes.data;
                const fetchedPrereqs: Prerequisite[] = prereqRes.data.data || prereqRes.data;

                setCourses(fetchedCourses);

                // Filtramos solo los prerrequisitos de esta malla
                const courseIds = new Set(fetchedCourses.map((c) => c.public_id));
                setPrerequisites(fetchedPrereqs.filter((p) => courseIds.has(p.course)));
            } catch (error) {
                console.error('Error al cargar la malla:', error);
                if (mounted) toast.error('No pudimos cargar tu malla curricular.');
            } finally {
                if (mounted) setIsLoading(false);
            }
        };

        fetchCurriculumData();

        return () => {
            mounted = false;
        };
    }, [planId]);

    const coursesByCycle = courses.reduce(
        (acc, course) => {
            const cycle = course.cycle;
            if (!acc[cycle]) acc[cycle] = [];
            acc[cycle].push(course);
            return acc;
        },
        {} as Record<number, Course[]>,
    );

    return {
        courses,
        coursesByCycle,
        prerequisites,
        isLoading,
        planId,
    };
}
