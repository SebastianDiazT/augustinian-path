import type { PropsWithChildren } from 'react';

import { CircleAlert, LoaderCircle } from 'lucide-react';

import { BrandLogo } from '@/components/brand/brand-logo';
import { ThemeMenu } from '@/theme/theme-menu';

interface AuthStateScreenProps extends PropsWithChildren {
    description: string;
    title: string;
    tone?: 'loading' | 'error';
}

export function AuthStateScreen({
    children,
    description,
    title,
    tone = 'loading',
}: AuthStateScreenProps) {
    const Icon = tone === 'loading' ? LoaderCircle : CircleAlert;

    return (
        <main className='min-h-screen bg-background px-5 py-6 text-foreground sm:px-8'>
            <header className='mx-auto flex max-w-6xl items-center justify-between gap-4'>
                <BrandLogo showTagline={false} />
                <ThemeMenu />
            </header>

            <section className='mx-auto flex min-h-[calc(100vh-8rem)] max-w-lg items-center'>
                <div className='w-full rounded-3xl border border-border bg-surface p-7 shadow-card sm:p-9'>
                    <span
                        className={
                            'inline-flex size-12 items-center justify-center rounded-2xl ' +
                            (tone === 'error'
                                ? 'bg-primary/10 text-primary'
                                : 'bg-accent/20 text-accent-foreground')
                        }
                    >
                        <Icon
                            className={
                                'size-6 ' +
                                (tone === 'loading' ? 'motion-safe:animate-spin' : '')
                            }
                            aria-hidden='true'
                        />
                    </span>

                    <h1 className='mt-6 font-display text-2xl font-extrabold tracking-[-0.035em] sm:text-3xl'>
                        {title}
                    </h1>

                    <p className='mt-3 leading-7 text-muted-foreground'>
                        {description}
                    </p>

                    {children ? <div className='mt-7'>{children}</div> : null}
                </div>
            </section>
        </main>
    );
}
