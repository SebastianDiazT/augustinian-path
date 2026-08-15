import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

export interface PublicDocumentSection {
    id: string;
    title: string;
    content: ReactNode;
}

interface PublicDocumentLayoutProps {
    eyebrow?: string;
    title: string;
    description: string;
    sections: PublicDocumentSection[];
    className?: string;
}

export function PublicDocumentLayout({
    eyebrow,
    title,
    description,
    sections,
    className,
}: PublicDocumentLayoutProps) {
    return (
        <div className={cn('mx-auto max-w-3xl px-4 py-16 sm:px-6 sm:py-24 lg:py-32', className)}>
            <header className='mb-12 animate-reveal-soft opacity-0 sm:mb-16'>
                {eyebrow && (
                    <span className='mb-4 inline-flex items-center rounded-full bg-primary/10 px-3 py-1.5 text-xs font-extrabold uppercase tracking-widest text-primary dark:bg-primary/20'>
                        {eyebrow}
                    </span>
                )}
                <h1 className='font-display text-4xl font-extrabold tracking-tight text-foreground sm:text-5xl'>
                    {title}
                </h1>
                <p className='mt-4 text-lg leading-relaxed text-muted-foreground sm:text-xl'>
                    {description}
                </p>
            </header>

            <div className='space-y-6 sm:space-y-8'>
                {sections.map((section, index) => (
                    <section
                        key={section.id}
                        id={section.id}
                        className='scroll-mt-24 rounded-3xl border border-border bg-surface p-6 shadow-sm transition-shadow hover:shadow-md sm:scroll-mt-32 sm:p-8 animate-reveal-soft opacity-0'
                        style={{ animationDelay: `${(index + 1) * 100}ms` }}
                    >
                        <h2 className='mb-4 text-xl font-extrabold text-foreground sm:text-2xl'>
                            {section.title}
                        </h2>

                        <div className='flex flex-col gap-4 text-[0.95rem] leading-relaxed text-muted-foreground sm:text-base'>
                            {section.content}
                        </div>
                    </section>
                ))}
            </div>
        </div>
    );
}
