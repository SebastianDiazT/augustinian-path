import { Link } from 'react-router-dom';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { GoogleLogin } from '@react-oauth/google';
import { toast } from 'sonner';

import { publicPaths } from '@/app/paths';
import { SEO } from '@/components/seo';
import { BrandLogo } from '@/components/brand/brand-logo';
import { LoginBackgroundMesh } from '@/components/marketing/login-background';
import { useLogin } from '@/hooks/use-login';

export default function LoginPage() {
    const { handleGoogleSuccess, isLoading, dict } = useLogin();

    return (
        <div className='relative flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8 overflow-hidden'>
            <SEO title={dict.seo.title} description={dict.seo.description} />
            <LoginBackgroundMesh />

            <div className='absolute inset-0 z-0 pointer-events-none overflow-hidden'>
                <div className='absolute top-1/4 left-[10%] size-150 rounded-full bg-primary/10 blur-[120px] dark:bg-primary/15' />
                <div className='absolute bottom-1/4 right-[10%] size-150 rounded-full bg-accent/10 blur-[120px] dark:bg-accent/15' />
            </div>

            <div className='relative z-10 w-full max-w-md animate-reveal-soft'>
                <div className='rounded-3xl border border-border/60 bg-background/85 p-8 shadow-[0_0_50px_rgba(0,0,0,0.1)] backdrop-blur-2xl sm:p-10 dark:shadow-[0_0_50px_rgba(0,0,0,0.5)]'>
                    <div className='mb-10 flex items-center justify-between'>
                        <BrandLogo showTagline={false} />
                        <Link
                            to={publicPaths.home}
                            className='group flex size-10 items-center justify-center rounded-full border border-border bg-surface transition-colors hover:bg-surface-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary'
                            aria-label={dict.backToHome}
                        >
                            <ArrowLeft className='size-4 text-muted-foreground transition-transform group-hover:-translate-x-0.5' />
                        </Link>
                    </div>

                    <div className='mb-10'>
                        <h2 className='font-display text-2xl font-extrabold tracking-tight text-foreground sm:text-3xl'>
                            {dict.title}
                        </h2>
                        <p className='mt-3 text-sm leading-relaxed text-muted-foreground'>
                            {dict.subtitle}
                        </p>
                    </div>

                    <div>
                        {isLoading ? (
                            <div className='flex h-11 w-full items-center justify-center rounded-full border border-border bg-surface shadow-sm'>
                                <Loader2
                                    className='size-5 animate-spin text-primary'
                                    aria-hidden='true'
                                />
                            </div>
                        ) : (
                            <div className='flex justify-center transition-opacity hover:opacity-90'>
                                <GoogleLogin
                                    onSuccess={handleGoogleSuccess}
                                    onError={() => toast.error(dict.errors.default)}
                                    theme='outline'
                                    size='large'
                                    text='continue_with'
                                    shape='pill'
                                />
                            </div>
                        )}
                    </div>
                </div>

                <p className='mt-8 text-center text-xs font-semibold text-muted-foreground/90 backdrop-blur-sm'>
                    Al iniciar sesión, aceptas nuestra{' '}
                    <Link to={publicPaths.privacy} className='text-primary hover:underline'>
                        política de privacidad
                    </Link>
                    .
                </p>
            </div>
        </div>
    );
}
