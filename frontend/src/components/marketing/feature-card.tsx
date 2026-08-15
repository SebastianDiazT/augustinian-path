import type { LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface FeatureCardProps {
    title: string;
    description: string;
    icon: LucideIcon;
    className?: string;
    style?: React.CSSProperties;
}

export function FeatureCard({
    title,
    description,
    icon: Icon,
    className,
    style,
}: FeatureCardProps) {
    return (
        <article
            className={cn(
                'group relative isolate h-full overflow-hidden rounded-3xl border border-border bg-surface p-7 shadow-card transition-all duration-300 hover:-translate-y-1 hover:border-primary/30 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] dark:hover:shadow-[0_8px_30px_rgb(0,0,0,0.4)] sm:p-8',
                className,
            )}
            style={style}
        >
            <span
                className='pointer-events-none absolute inset-x-8 top-0 h-px bg-linear-to-r from-transparent via-primary/30 to-transparent'
                aria-hidden='true'
            />

            <span className='inline-flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary transition-transform duration-300 group-hover:scale-110 group-hover:bg-primary/15 dark:bg-primary/20 dark:group-hover:bg-primary/30'>
                <Icon className='size-6' aria-hidden='true' />
            </span>

            <h3 className='mt-6 font-display text-xl font-extrabold tracking-tight text-foreground sm:text-2xl'>
                {title}
            </h3>

            <p className='mt-3 text-[0.95rem] leading-relaxed text-muted-foreground'>
                {description}
            </p>
        </article>
    );
}
