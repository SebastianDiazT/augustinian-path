import type { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';
import { ES_UI } from '@/locales/es';
import logoMarkUrl from '@/assets/logo-mark.svg';

interface BrandLogoProps extends HTMLAttributes<HTMLDivElement> {
    showTagline?: boolean;
}

export function BrandLogo({ showTagline = true, className, ...props }: BrandLogoProps) {
    return (
        <div className={cn('inline-flex items-center gap-3', className)} {...props}>
            <span className='inline-flex size-10 shrink-0 items-center justify-center rounded-xl bg-primary/10 text-primary transition-colors dark:bg-white dark:text-primary'>
                <img src={logoMarkUrl} alt='' className='size-7 object-contain' />
            </span>

            <span className='h-8 w-px bg-border' aria-hidden='true' />

            <span className='min-w-0'>
                <span className='block font-display text-lg font-extrabold tracking-tight'>
                    <span className='text-primary dark:text-white'>Ruta</span>{' '}
                    <span className='text-foreground'>Agustina</span>
                </span>

                {showTagline && (
                    <span className='block text-[0.65rem] font-bold uppercase tracking-widest text-muted-foreground'>
                        {ES_UI.brand.tagline}
                    </span>
                )}
            </span>
        </div>
    );
}
