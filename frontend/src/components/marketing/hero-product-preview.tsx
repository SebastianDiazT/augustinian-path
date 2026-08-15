import { CalendarDays, CheckCircle2, Clock3, GraduationCap, Sparkles } from 'lucide-react';
import { ES_UI } from '@/locales/es';

// Datos de demostración
const selectedCourses = [
    { name: 'Cálculo en varias variables', credits: 4 },
    { name: 'Estructuras de datos', credits: 4 },
    { name: 'Estadística aplicada', credits: 3 },
];

const schedule = [
    { day: 'Lun', subject: 'Cálculo', time: '08:00' },
    { day: 'Mié', subject: 'Estructuras', time: '10:00' },
    { day: 'Vie', subject: 'Estadística', time: '14:00' },
];

const totalCredits = selectedCourses.reduce((total, course) => total + course.credits, 0);

export function HeroProductPreview() {
    const currentYear = new Date().getFullYear();

    return (
        <section
            className='animate-reveal-soft-delayed relative isolate overflow-hidden rounded-4xl border border-border bg-surface p-4 shadow-card sm:p-5 opacity-0'
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

            <div className='relative rounded-3xl border border-border bg-background/70 p-4 sm:p-5 backdrop-blur-sm'>
                <header className='flex flex-wrap items-center justify-between gap-4 border-b border-border pb-4'>
                    <div className='flex min-w-0 items-center gap-3'>
                        <span className='inline-flex size-11 shrink-0 items-center justify-center rounded-2xl bg-primary text-primary-foreground shadow-sm'>
                            <CalendarDays className='size-5' aria-hidden='true' />
                        </span>

                        <div className='min-w-0'>
                            <p className='flex items-center gap-1.5 text-xs font-bold uppercase tracking-[0.12em] text-primary'>
                                <Sparkles className='size-3.5' aria-hidden='true' />
                                {ES_UI.marketing.preview.badge}
                            </p>
                            <p className='mt-1 truncate text-sm font-extrabold sm:text-base'>
                                {ES_UI.marketing.preview.title.replace(
                                    '{year}',
                                    currentYear.toString(),
                                )}
                            </p>
                        </div>
                    </div>

                    <span className='inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1.5 text-xs font-bold text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-300'>
                        <CheckCircle2 className='size-4' aria-hidden='true' />
                        {ES_UI.marketing.preview.status}
                    </span>
                </header>

                <div className='mt-4 grid gap-4 lg:grid-cols-[0.9fr_1.25fr]'>
                    <section className='rounded-2xl bg-surface-muted p-4 sm:p-5'>
                        <div className='flex items-center justify-between gap-3'>
                            <div className='flex items-center gap-2'>
                                <GraduationCap className='size-5 text-primary' aria-hidden='true' />
                                <h2 className='text-sm font-extrabold'>
                                    {ES_UI.marketing.preview.selectedCourses}
                                </h2>
                            </div>

                            <span className='text-xs font-semibold text-muted-foreground'>
                                {ES_UI.marketing.preview.credits.replace(
                                    '{count}',
                                    totalCredits.toString(),
                                )}
                            </span>
                        </div>

                        <ul className='mt-4 space-y-2.5'>
                            {selectedCourses.map((course, index) => (
                                <li
                                    key={course.name}
                                    className='flex items-center gap-3 rounded-xl border border-border bg-surface p-3 shadow-sm transition-transform hover:scale-[1.02]'
                                >
                                    <span className='inline-flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary/10 text-xs font-extrabold text-primary'>
                                        {index + 1}
                                    </span>

                                    <div className='min-w-0'>
                                        <p className='text-xs font-bold leading-5 sm:text-sm truncate'>
                                            {course.name}
                                        </p>
                                        <p className='mt-0.5 text-xs text-muted-foreground'>
                                            {ES_UI.marketing.preview.credits.replace(
                                                '{count}',
                                                course.credits.toString(),
                                            )}
                                        </p>
                                    </div>
                                </li>
                            ))}
                        </ul>
                    </section>

                    <section className='rounded-2xl border border-border bg-surface p-4 sm:p-5'>
                        <div className='flex items-center justify-between gap-3'>
                            <h2 className='text-sm font-extrabold'>
                                {ES_UI.marketing.preview.schedule}
                            </h2>

                            <span className='inline-flex items-center gap-1.5 text-xs font-semibold text-muted-foreground'>
                                <Clock3 className='size-4' aria-hidden='true' />
                                {ES_UI.marketing.preview.hours.replace('{count}', '15')}
                            </span>
                        </div>

                        <ul className='mt-4 grid grid-cols-1 gap-2.5 min-[420px]:grid-cols-3'>
                            {schedule.map((course) => (
                                <li
                                    key={`${course.day}-${course.subject}`}
                                    className='min-w-0 rounded-xl border border-primary/15 bg-primary/5 p-3 dark:bg-primary/10'
                                >
                                    <p className='text-xs font-extrabold uppercase tracking-widest text-primary'>
                                        {course.day}
                                    </p>
                                    <p className='mt-2 text-xs font-bold leading-5 sm:text-sm truncate'>
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
                                <span className='font-bold'>
                                    {ES_UI.marketing.preview.progress}
                                </span>
                                <span className='font-semibold text-muted-foreground'>68%</span>
                            </div>

                            <div
                                className='mt-2 h-2.5 overflow-hidden rounded-full bg-surface-muted'
                                role='progressbar'
                                aria-label={ES_UI.marketing.preview.progress}
                                aria-valuemin={0}
                                aria-valuemax={100}
                                aria-valuenow={68}
                            >
                                <div
                                    className='animate-progress-grow h-full rounded-full bg-primary opacity-0'
                                    style={{ width: '68%' }}
                                />
                            </div>
                        </div>

                        <div className='mt-4 flex items-center gap-2 rounded-xl border border-accent/40 bg-accent/10 p-3'>
                            <CheckCircle2
                                className='size-4 shrink-0 text-accent-foreground dark:text-accent'
                                aria-hidden='true'
                            />
                            <p className='text-xs font-bold text-accent-foreground dark:text-accent'>
                                {ES_UI.marketing.preview.readyMessage.replace(
                                    '{count}',
                                    selectedCourses.length.toString(),
                                )}
                            </p>
                        </div>
                    </section>
                </div>
            </div>
        </section>
    );
}
