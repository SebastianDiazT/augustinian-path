import type { HTMLAttributes } from 'react';

import { BrandMark } from '@/components/brand/brand-mark';

interface BrandLogoProps extends HTMLAttributes<HTMLDivElement> {
    inverse?: boolean;
    showTagline?: boolean;
}

export function BrandLogo({
    inverse = false,
    showTagline = true,
    className = '',
    ...props
}: BrandLogoProps) {
    const primaryTextClass = inverse ? 'text-white' : 'text-primary';

    const secondaryTextClass = inverse ? 'text-white' : 'text-foreground';

    const taglineClass = inverse ? 'text-white/65' : 'text-muted-foreground';

    return (
        <div className={`inline-flex items-center gap-3 ${className}`} {...props}>
            <span
                className={
                    'inline-flex size-12 shrink-0 items-center justify-center rounded-2xl ' +
                    (inverse ? 'bg-white' : 'bg-surface-muted')
                }
            >
                <BrandMark alt='' className='size-10' />
            </span>

            <span className='h-10 w-px bg-accent' aria-hidden='true' />

            <span className='min-w-0'>
                <span className='block font-display text-lg font-extrabold tracking-[-0.035em]'>
                    <span className={primaryTextClass}>Ruta</span>{' '}
                    <span className={secondaryTextClass}>Agustina</span>
                </span>

                {showTagline ? (
                    <span className={`block text-xs ${taglineClass}`}>
                        Planificación académica
                    </span>
                ) : null}
            </span>
        </div>
    );
}
