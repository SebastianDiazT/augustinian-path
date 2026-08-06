import type { LucideIcon } from 'lucide-react';

interface FeatureCardProps {
    description: string;
    icon: LucideIcon;
    title: string;
}

export function FeatureCard({ description, icon: Icon, title }: FeatureCardProps) {
    return (
        <article className='group relative isolate h-full overflow-hidden rounded-[1.75rem] border border-border bg-surface p-7 shadow-sm transition-[transform,box-shadow,border-color] duration-300 ease-out motion-safe:hover:-translate-y-0.5 motion-safe:hover:border-primary/25 motion-safe:hover:shadow-card sm:p-8'>
            <span
                className='pointer-events-none absolute inset-x-8 top-0 h-px bg-linear-to-r from-transparent via-primary/40 to-transparent'
                aria-hidden='true'
            />

            <span className='inline-flex size-13 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-[transform,background-color] duration-300 motion-safe:group-hover:scale-105 motion-safe:group-hover:bg-primary/15'>
                <Icon className='size-6' aria-hidden='true' />
            </span>

            <h3 className='mt-6 text-pretty font-display text-xl font-extrabold tracking-tight sm:text-2xl'>
                {title}
            </h3>

            <p className='mt-3 text-[0.95rem] leading-7 text-muted-foreground'>
                {description}
            </p>
        </article>
    );
}
