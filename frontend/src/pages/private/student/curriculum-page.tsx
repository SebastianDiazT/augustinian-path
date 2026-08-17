import { useState, useMemo } from 'react';
import {
    BookOpen,
    FlaskConical,
    AlertCircle,
    Loader2,
    Network,
    List,
    LayoutGrid,
    Search,
} from 'lucide-react';
import { SEO } from '@/components/seo';
import { useCurriculum } from '@/hooks/use-curriculum'; // <-- Se quitó "type Course"

const CYCLES = Array.from({ length: 10 }, (_, i) => i + 1);

type ViewMode = 'graph' | 'kanban' | 'list';

export default function CurriculumPage() {
    const { courses, coursesByCycle, prerequisites, isLoading, planId } = useCurriculum();
    const [viewMode, setViewMode] = useState<ViewMode>('graph');

    const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
    const [searchQuery, setSearchQuery] = useState('');

    const { highlightedPrereqs, highlightedUnlocks } = useMemo(() => {
        if (!selectedCourseId)
            return { highlightedPrereqs: new Set(), highlightedUnlocks: new Set() };

        const prereqs = new Set<string>();
        const unlocks = new Set<string>();

        prerequisites.forEach((p) => {
            if (p.course === selectedCourseId) prereqs.add(p.required_course);
        });

        prerequisites.forEach((p) => {
            if (p.required_course === selectedCourseId) unlocks.add(p.course);
        });

        return { highlightedPrereqs: prereqs, highlightedUnlocks: unlocks };
    }, [selectedCourseId, prerequisites]);

    const handleContainerClick = () => setSelectedCourseId(null);

    if (isLoading) {
        return (
            <div className='flex h-[60vh] items-center justify-center'>
                <div className='flex flex-col items-center gap-4 text-muted-foreground'>
                    <Loader2 className='size-8 animate-spin text-primary' />
                    <p className='font-medium'>Construyendo tu plan de estudios...</p>
                </div>
            </div>
        );
    }

    if (!planId) {
        return (
            <div className='flex h-[60vh] items-center justify-center'>
                <div className='flex max-w-md flex-col items-center text-center'>
                    <div className='mb-4 flex size-12 items-center justify-center rounded-full bg-amber-500/10 text-amber-500'>
                        <AlertCircle className='size-6' />
                    </div>
                    <h2 className='text-lg font-bold text-foreground'>Sin Plan Asignado</h2>
                    <p className='mt-2 text-sm text-muted-foreground'>
                        Tu perfil aún no tiene un plan de estudios activo.
                    </p>
                </div>
            </div>
        );
    }

    const filteredCourses = courses.filter(
        (c) =>
            c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            c.code.toLowerCase().includes(searchQuery.toLowerCase()),
    );

    return (
        <div className='flex h-full flex-col animate-reveal-soft' onClick={handleContainerClick}>
            <SEO title='Malla Curricular' description='Visualiza tu plan de estudios' />

            <div className='mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between shrink-0'>
                <div>
                    <h1 className='font-display text-2xl font-extrabold tracking-tight text-foreground sm:text-3xl'>
                        Malla Curricular
                    </h1>
                    <p className='mt-2 text-sm text-muted-foreground'>
                        {viewMode === 'graph'
                            ? 'Haz clic en un curso para ver sus prerrequisitos y las materias que desbloquea.'
                            : 'Explora y busca asignaturas de tu plan.'}
                    </p>
                </div>

                <div className='flex items-center rounded-xl border border-border bg-surface/50 p-1 backdrop-blur-sm'>
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            setViewMode('graph');
                        }}
                        className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${viewMode === 'graph' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
                    >
                        <Network className='size-4' />{' '}
                        <span className='hidden sm:inline'>Grafo</span>
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            setViewMode('kanban');
                        }}
                        className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${viewMode === 'kanban' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
                    >
                        <LayoutGrid className='size-4' />{' '}
                        <span className='hidden sm:inline'>Tablero</span>
                    </button>
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            setViewMode('list');
                        }}
                        className={`flex items-center gap-2 rounded-lg px-3 py-1.5 text-sm font-medium transition-all ${viewMode === 'list' ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'}`}
                    >
                        <List className='size-4' /> <span className='hidden sm:inline'>Lista</span>
                    </button>
                </div>
            </div>

            {(viewMode === 'graph' || viewMode === 'kanban') && (
                <div className='flex-1 overflow-x-auto pb-6 custom-scrollbar'>
                    <div className='inline-flex h-full min-w-full gap-6 px-1'>
                        {CYCLES.map((cycle) => {
                            const cycleCourses = coursesByCycle[cycle] || [];
                            return (
                                <div
                                    key={cycle}
                                    className='flex w-72 shrink-0 flex-col rounded-2xl bg-surface/30 border border-border/50 p-4'
                                >
                                    <div className='mb-4 flex items-center justify-between border-b border-border/50 pb-3'>
                                        <h2 className='font-bold text-foreground'>
                                            Semestre {cycle}
                                        </h2>
                                    </div>

                                    <div className='flex flex-1 flex-col gap-3 overflow-y-auto custom-scrollbar pr-1'>
                                        {cycleCourses.map((course) => {
                                            const isSelected =
                                                selectedCourseId === course.public_id;
                                            const isPrereq = highlightedPrereqs.has(
                                                course.public_id,
                                            );
                                            const isUnlock = highlightedUnlocks.has(
                                                course.public_id,
                                            );
                                            const isDimmed =
                                                viewMode === 'graph' &&
                                                selectedCourseId &&
                                                !isSelected &&
                                                !isPrereq &&
                                                !isUnlock;

                                            return (
                                                <div
                                                    key={course.public_id}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        if (viewMode === 'graph') {
                                                            setSelectedCourseId(
                                                                isSelected
                                                                    ? null
                                                                    : course.public_id,
                                                            );
                                                        }
                                                    }}
                                                    className={`group relative flex flex-col rounded-xl border p-3.5 transition-all duration-300
                                                        ${viewMode === 'graph' ? 'cursor-pointer' : ''}
                                                        ${isDimmed ? 'opacity-30 grayscale border-border/30 bg-background/50' : 'bg-background shadow-sm hover:shadow-md'}
                                                        ${isSelected ? 'border-primary ring-2 ring-primary/20 bg-primary/5' : ''}
                                                        ${isPrereq ? 'border-amber-500 bg-amber-500/5' : ''}
                                                        ${isUnlock ? 'border-emerald-500 bg-emerald-500/5' : ''}
                                                        ${!isSelected && !isPrereq && !isUnlock && !isDimmed ? 'border-border hover:border-primary/30' : ''}
                                                    `}
                                                >
                                                    <div className='mb-2 flex items-center justify-between'>
                                                        <span className='text-[0.65rem] font-bold uppercase tracking-wider text-muted-foreground'>
                                                            {course.code}
                                                        </span>
                                                        {course.course_type === 'elective' && (
                                                            <span className='rounded-md bg-amber-500/10 px-1.5 py-0.5 text-[0.65rem] font-bold text-amber-600 dark:text-amber-400'>
                                                                ELECTIVO
                                                            </span>
                                                        )}
                                                    </div>

                                                    <h3 className='mb-3 text-sm font-bold leading-snug text-foreground line-clamp-3'>
                                                        {course.name}
                                                    </h3>

                                                    <div className='mt-auto flex items-center justify-between border-t border-border/40 pt-2.5'>
                                                        <div className='flex items-center gap-1.5 text-xs font-medium text-muted-foreground'>
                                                            <BookOpen className='size-3.5' />
                                                            <span>
                                                                {Number(course.credits)} cred.
                                                            </span>
                                                        </div>
                                                        {course.has_lab && (
                                                            // <-- AQUÍ ENVUELVO EL ICONO PARA CUMPLIR CON TS
                                                            <span
                                                                title='Laboratorio'
                                                                className='flex items-center text-blue-500'
                                                            >
                                                                <FlaskConical className='size-3.5' />
                                                            </span>
                                                        )}
                                                    </div>

                                                    {isPrereq && (
                                                        <span className='absolute -top-2.5 right-3 bg-amber-500 text-white text-[0.6rem] font-bold px-2 py-0.5 rounded-full shadow-sm'>
                                                            Requiere
                                                        </span>
                                                    )}
                                                    {isUnlock && (
                                                        <span className='absolute -top-2.5 right-3 bg-emerald-500 text-white text-[0.6rem] font-bold px-2 py-0.5 rounded-full shadow-sm'>
                                                            Desbloquea
                                                        </span>
                                                    )}
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}

            {viewMode === 'list' && (
                <div className='flex-1 overflow-hidden flex flex-col bg-surface/50 border border-border rounded-2xl p-4 sm:p-6'>
                    <div className='relative mb-6'>
                        <Search className='absolute left-3 top-1/2 -translate-y-1/2 size-5 text-muted-foreground' />
                        <input
                            type='text'
                            placeholder='Buscar asignatura por nombre o código...'
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className='w-full rounded-xl border border-border bg-background py-3 pl-10 pr-4 text-sm focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20'
                        />
                    </div>

                    <div className='flex-1 overflow-y-auto custom-scrollbar'>
                        <div className='grid gap-3 sm:grid-cols-2 lg:grid-cols-3'>
                            {filteredCourses.map((course) => (
                                <div
                                    key={course.public_id}
                                    className='flex items-center gap-4 rounded-xl border border-border bg-background p-4'
                                >
                                    <div className='flex size-12 shrink-0 items-center justify-center rounded-full bg-primary/10 font-display text-lg font-bold text-primary'>
                                        {course.cycle}
                                    </div>
                                    <div className='min-w-0 flex-1'>
                                        <p
                                            className='truncate text-sm font-bold text-foreground'
                                            title={course.name}
                                        >
                                            {course.name}
                                        </p>
                                        <p className='text-xs text-muted-foreground'>
                                            {course.code} • {Number(course.credits)} Créditos
                                        </p>
                                    </div>
                                </div>
                            ))}
                            {filteredCourses.length === 0 && (
                                <p className='col-span-full py-10 text-center text-sm text-muted-foreground'>
                                    No se encontraron cursos.
                                </p>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
