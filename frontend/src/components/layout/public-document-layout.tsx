import { ArrowLeft, CalendarClock, Mail } from 'lucide-react';
import type { ReactNode } from 'react';
import { Link } from 'react-router';

import { publicPaths } from '@/app/paths';
import { projectConfig } from '@/config/project';

export interface PublicDocumentSection {
    content: ReactNode;
    id: string;
    title: string;
}

interface PublicDocumentLayoutProps {
    description: string;
    eyebrow: string;
    sections: PublicDocumentSection[];
    title: string;
}

export function PublicDocumentLayout({
    description,
    eyebrow,
    sections,
    title,
}: PublicDocumentLayoutProps) {
    return (
        <article className='px-4 py-12 sm:px-6 sm:py-16 lg:py-20'>
            <div className='mx-auto w-full max-w-6xl'>
                <Link
                    to={publicPaths.home}
                    className='inline-flex min-h-10 items-center gap-2 rounded-lg text-sm font-bold text-muted-foreground transition-colors hover:text-primary focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'
                >
                    <ArrowLeft className='size-4' aria-hidden='true' />
                    Volver al inicio
                </Link>

                <header className='mt-8 overflow-hidden rounded-4xl border border-border bg-surface p-6 shadow-sm sm:p-8 lg:p-10'>
                    <p className='text-xs font-extrabold uppercase tracking-[0.16em] text-primary'>
                        {eyebrow}
                    </p>

                    <h1 className='mt-4 max-w-4xl text-balance font-display text-3xl font-extrabold tracking-[-0.04em] sm:text-4xl lg:text-5xl'>
                        {title}
                    </h1>

                    <p className='mt-5 max-w-3xl text-pretty leading-7 text-muted-foreground sm:text-lg sm:leading-8'>
                        {description}
                    </p>

                    <div className='mt-6 inline-flex items-center gap-2 rounded-full border border-border bg-background px-3 py-1.5 text-xs font-bold text-muted-foreground'>
                        <CalendarClock
                            className='size-4 text-primary'
                            aria-hidden='true'
                        />
                        Actualizado el {projectConfig.legalUpdatedAt}
                    </div>
                </header>

                <div className='mt-10 grid items-start gap-10 lg:grid-cols-[15rem_minmax(0,1fr)] lg:gap-14'>
                    <aside className='rounded-2xl border border-border bg-surface p-5 lg:sticky lg:top-28'>
                        <nav aria-label='Contenido de esta página'>
                            <h2 className='text-xs font-extrabold uppercase tracking-[0.14em] text-foreground'>
                                Contenido
                            </h2>

                            <ol className='mt-4 space-y-1'>
                                {sections.map((section, index) => (
                                    <li key={section.id}>
                                        <a
                                            href={`#${section.id}`}
                                            className='flex min-h-10 items-start gap-3 rounded-lg px-2 py-2 text-sm leading-5 text-muted-foreground transition-colors hover:bg-surface-muted hover:text-primary focus-visible:outline-2 focus-visible:outline-primary'
                                        >
                                            <span
                                                className='font-bold text-primary'
                                                aria-hidden='true'
                                            >
                                                {index + 1}.
                                            </span>

                                            {section.title}
                                        </a>
                                    </li>
                                ))}
                            </ol>
                        </nav>
                    </aside>

                    <div className='space-y-12'>
                        {sections.map((section) => (
                            <section
                                key={section.id}
                                id={section.id}
                                className='scroll-mt-28'
                                aria-labelledby={`${section.id}-title`}
                            >
                                <h2
                                    id={`${section.id}-title`}
                                    className='font-display text-2xl font-extrabold tracking-tight sm:text-3xl'
                                >
                                    {section.title}
                                </h2>

                                <div className='mt-4 space-y-4 text-[0.95rem] leading-7 text-muted-foreground'>
                                    {section.content}
                                </div>
                            </section>
                        ))}

                        <div className='rounded-2xl border border-primary/15 bg-primary/6 p-5 sm:p-6'>
                            <div className='flex items-start gap-3'>
                                <span className='inline-flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary'>
                                    <Mail className='size-5' aria-hidden='true' />
                                </span>

                                <div>
                                    <h2 className='font-display text-lg font-extrabold'>
                                        ¿Necesitas comunicarte con nosotros?
                                    </h2>

                                    <p className='mt-2 text-sm leading-6 text-muted-foreground'>
                                        Escríbenos a{' '}
                                        <a
                                            href={`mailto:${projectConfig.supportEmail}`}
                                            className='font-bold text-primary underline-offset-4 hover:underline'
                                        >
                                            {projectConfig.supportEmail}
                                        </a>
                                        .
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </article>
    );
}
