import type { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import { ES_UI } from '@/locales/es';
import { BrandMark } from '@/components/brand/brand-mark';

interface BrandLogoProps extends HTMLAttributes<HTMLDivElement> {
    inverse?: boolean;
    showTagline?: boolean;
}

export function BrandLogo({
    inverse = false,
    showTagline = true,
    className,
    ...props
}: BrandLogoProps) {
    const [firstName, lastName] = ES_UI.brand.name.split(' ');

    const primaryTextClass = inverse ? 'text-white' : 'text-primary dark:text-white';
    const secondaryTextClass = inverse ? 'text-white' : 'text-foreground';
    const taglineClass = inverse ? 'text-white/65' : 'text-muted-foreground';

    return (
        <div className={cn('inline-flex items-center gap-3', className)} {...props}>
            <span
                className={cn(
                    'inline-flex size-12 shrink-0 items-center justify-center rounded-2xl',
                    inverse ? 'bg-white' : 'bg-surface-muted dark:bg-white/10',
                )}
            >
                <BrandMark alt='' className='size-10' />
            </span>

            <span className='h-10 w-px bg-accent' aria-hidden='true' />

            <span className='min-w-0'>
                <span className='block font-display text-lg font-extrabold tracking-[-0.035em]'>
                    <span className={primaryTextClass}>{firstName}</span>{' '}
                    <span className={secondaryTextClass}>{lastName}</span>
                </span>

                {showTagline && (
                    <span className={cn('block text-xs font-semibold', taglineClass)}>
                        {ES_UI.brand.tagline}
                    </span>
                )}
            </span>
        </div>
    );
}
