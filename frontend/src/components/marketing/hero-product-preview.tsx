import {
    CalendarDays,
    CheckCircle2,
    Clock3,
    GraduationCap,
    Sparkles,
} from 'lucide-react';

const selectedCourses = [
    {
        name: 'Cálculo en varias variables',
        credits: 4,
    },
    {
        name: 'Estructuras de datos',
        credits: 4,
    },
    {
        name: 'Estadística aplicada',
        credits: 3,
    },
];

const schedule = [
    {
        day: 'Lun',
        subject: 'Cálculo',
        time: '08:00',
    },
    {
        day: 'Mié',
        subject: 'Estructuras',
        time: '10:00',
    },
    {
        day: 'Vie',
        subject: 'Estadística',
        time: '14:00',
    },
];

const totalCredits = selectedCourses.reduce(
    (total, course) => total + course.credits,
    0,
);

export function HeroProductPreview() {
    return (
        <section
            className='animate-reveal-soft-delayed relative isolate overflow-hidden rounded-4xl border border-border bg-surface p-4 shadow-card sm:p-5'
            aria-label='Vista previa de la planificación académica'
        >
            <span
                className='pointer-events-none absolute -right-16 -top-16 size-48 rounded-full bg-primary/10 blur-3xl'
                aria-hidden='true'
            />
            <span
                className='pointer-events-none absolute -bottom-20 -left-16 size-48 rounded-full bg-accent/10 blur-3xl'
                aria-hidden='true'
            />

            <div className='relative rounded-3xl border border-border bg-background/70 p-4 sm:p-5'>
                <header className='flex flex-wrap items-center justify-between gap-4 border-b border-border pb-4'>
                    <div className='flex min-w-0 items-center gap-3'>
                        <span className='inline-flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm'>
                            <CalendarDays className='size-5' aria-hidden='true' />
                        </span>

                        <div className='min-w-0'>
                            <p className='flex items-center gap-1.5 text-xs font-bold uppercase tracking-[0.12em] text-primary'>
                                <Sparkles className='size-3.5' aria-hidden='true' />
                                Vista previa
                            </p>
                            <p className='mt-1 truncate text-sm font-extrabold sm:text-base'>
                                Planificación 2026
                            </p>
                        </div>
                    </div>

                    <span className='inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1.5 text-xs font-bold text-emerald-700 dark:text-emerald-300'>
                        <CheckCircle2 className='size-4' aria-hidden='true' />
                        Sin conflictos
                    </span>
                </header>

                <div className='mt-4 grid gap-4 lg:grid-cols-[0.9fr_1.25fr]'>
                    <section className='rounded-2xl bg-surface-muted p-4 sm:p-5'>
                        <div className='flex items-center justify-between gap-3'>
                            <div className='flex items-center gap-2'>
                                <GraduationCap
                                    className='size-5 text-primary'
                                    aria-hidden='true'
                                />
                                <h2 className='text-sm font-extrabold'>
                                    Cursos seleccionados
                                </h2>
                            </div>

                            <span className='text-xs font-semibold text-muted-foreground'>
                                {totalCredits} créditos
                            </span>
                        </div>

                        <ul className='animate-stagger-children mt-4 space-y-2.5'>
                            {selectedCourses.map((course, index) => (
                                <li
                                    key={course.name}
                                    className='flex items-center gap-3 rounded-xl border border-border bg-surface p-3 shadow-sm'
                                >
                                    <span className='inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-xs font-extrabold text-primary'>
                                        {index + 1}
                                    </span>

                                    <div className='min-w-0'>
                                        <p className='text-xs font-bold leading-5 sm:text-sm'>
                                            {course.name}
                                        </p>
                                        <p className='mt-0.5 text-xs text-muted-foreground'>
                                            {course.credits} créditos
                                        </p>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </section>

                    <section className='rounded-2xl border border-border bg-surface p-4 sm:p-5'>
                        <div className='flex items-center justify-between gap-3'>
                            <h2 className='text-sm font-extrabold'>Mi horario</h2>

                            <span className='inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground'>
                                <Clock3 className='size-4' aria-hidden='true' />
                                15 horas
                            </span>
                        </div>

                        <ul className='animate-stagger-children mt-4 grid grid-cols-1 gap-2.5 min-[420px]:grid-cols-3'>
                            {schedule.map((course) => (
                                <li
                                    key={`${course.day}-${course.subject}`}
                                    className='min-w-0 rounded-xl border border-primary/15 bg-primary/8 p-3'
                                >
                                    <p className='text-xs font-extrabold uppercase tracking-widest text-primary'>
                                        {' '}
                                        {course.day}
                                    </p>
                                    <p className='mt-2 text-xs font-bold leading-5 sm:text-sm'>
                                        {course.subject}
                                    </p>
                                    <p className='mt-1 text-xs text-muted-foreground'>
                                        {course.time}
                                    </p>
                                </li>
                            ))}
                        </ul>

                        <div className='mt-5'>
                            <div className='flex justify-between gap-3 text-xs'>
                                <span className='font-bold'>Progreso del plan</span>
                                <span className='font-semibold text-muted-foreground'>
                                    68%
                                </span>
                            </div>

                            <div
                                className='mt-2 h-2.5 overflow-hidden rounded-full bg-surface-muted'
                                role='progressbar'
                                aria-label='Progreso del plan de estudios'
                                aria-valuemin={0}
                                aria-valuemax={100}
                                aria-valuenow={68}
                            >
                                <div className='animate-progress-grow h-full w-[68%] rounded-full bg-primary' />
                            </div>
                        </div>

                        <div className='mt-4 flex items-center gap-2 rounded-xl border border-accent/40 bg-accent/10 p-3'>
                            <CheckCircle2
                                className='size-4 shrink-0 text-accent-foreground'
                                aria-hidden='true'
                            />
                            <p className='text-xs font-bold text-accent-foreground'>
                                3 cursos listos para generar tu horario
                            </p>
                        </div>
                    </section>
                </div>
            </div>
        </section>
    );
}
