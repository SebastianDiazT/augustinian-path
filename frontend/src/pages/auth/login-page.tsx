import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ArrowLeft, Loader2, CheckCircle2, Lock, Unlock } from 'lucide-react';
import { GoogleLogin, type CredentialResponse } from '@react-oauth/google';
import { jwtDecode } from 'jwt-decode';
import axios from 'axios';
import { toast } from 'sonner';
import { api } from '@/lib/api';
import { publicPaths } from '@/app/paths';
import { ES_UI } from '@/locales/es';
import { SEO } from '@/components/seo';
import { BrandLogo } from '@/components/brand/brand-logo';
import { useAuthStore } from '@/store/auth-store';

interface GoogleJwtPayload {
    email: string;
    name: string;
    picture: string;
}

function BackgroundNode({
    status,
    title,
    subtitle,
}: {
    status: 'done' | 'current' | 'locked';
    title: string;
    subtitle: string;
}) {
    const styles = {
        done: 'border-emerald-500/40 bg-emerald-500/10 text-emerald-600 dark:text-emerald-400/80 shadow-[0_0_15px_rgba(16,185,129,0.1)]',
        current:
            'border-primary/60 bg-primary/20 text-primary shadow-[0_0_40px_rgba(var(--primary),0.25)]',
        locked: 'border-foreground/20 bg-foreground/10 text-foreground/60',
    };

    const icons = {
        done: <CheckCircle2 className='size-4' />,
        current: <Unlock className='size-4' />,
        locked: <Lock className='size-4' />,
    };

    return (
        <div
            className={`flex w-56 flex-col gap-1.5 rounded-2xl border p-4 backdrop-blur-md transition-transform duration-700 hover:scale-105 ${styles[status]}`}
        >
            <div className='flex items-center gap-2'>
                {icons[status]}
                <span className='text-[10px] font-extrabold uppercase tracking-widest opacity-90'>
                    {subtitle}
                </span>
            </div>
            <p className='truncate text-sm font-bold'>{title}</p>
        </div>
    );
}

function BackgroundMeshWidget() {
    const dict = ES_UI.auth.login.previewWidget;

    return (
        <div
            className='absolute inset-0 z-0 flex items-center justify-center overflow-hidden pointer-events-none select-none opacity-70 dark:opacity-50'
            style={{
                maskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)',
                WebkitMaskImage: 'radial-gradient(circle at center, black 40%, transparent 100%)',
            }}
        >
            <div className='relative flex w-275 justify-between scale-[0.65] sm:scale-90 md:scale-110 lg:scale-[1.35] rotate-[-4deg] transition-transform duration-1000'>
                <svg className='absolute inset-0 size-full overflow-visible' style={{ zIndex: -1 }}>
                    <g
                        stroke='currentColor'
                        className='text-emerald-500/50'
                        strokeWidth='3'
                        fill='none'
                        strokeDasharray='6 6'
                    >
                        <path d='M 224 42 C 258 42, 258 42, 292 42' />
                        <path d='M 224 174 C 258 174, 258 42, 292 42' />
                        <path d='M 224 174 C 258 174, 258 174, 292 174' />
                        <path d='M 224 306 C 258 306, 258 174, 292 174' />
                        <path d='M 224 306 C 258 306, 258 306, 292 306' />
                    </g>

                    <g
                        stroke='currentColor'
                        className='text-primary/50'
                        strokeWidth='3'
                        fill='none'
                        strokeDasharray='6 6'
                    >
                        <path d='M 516 42 C 550 42, 550 42, 584 42' />
                        <path d='M 516 42 C 550 42, 550 174, 584 174' />
                        <path d='M 516 174 C 550 174, 550 174, 584 174' />
                        <path d='M 516 306 C 550 306, 550 174, 584 174' />
                        <path d='M 516 306 C 550 306, 550 306, 584 306' />
                    </g>

                    <g
                        stroke='currentColor'
                        className='text-foreground/20'
                        strokeWidth='3'
                        fill='none'
                    >
                        <path d='M 808 42 C 842 42, 842 42, 876 42' />
                        <path d='M 808 174 C 842 174, 842 42, 876 42' />
                        <path d='M 808 174 C 842 174, 842 174, 876 174' />
                        <path d='M 808 174 C 842 174, 842 306, 876 306' />
                        <path d='M 808 306 C 842 306, 842 306, 876 306' />
                    </g>
                </svg>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='done'
                        title={dict.nodes.done1}
                        subtitle={dict.status.done}
                    />
                    <BackgroundNode
                        status='done'
                        title={dict.nodes.done2}
                        subtitle={dict.status.done}
                    />
                    <BackgroundNode
                        status='done'
                        title={dict.nodes.done3}
                        subtitle={dict.status.done}
                    />
                </div>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='current'
                        title={dict.nodes.current1}
                        subtitle={dict.status.current}
                    />
                    <BackgroundNode
                        status='current'
                        title={dict.nodes.current2}
                        subtitle={dict.status.current}
                    />
                    <BackgroundNode
                        status='current'
                        title={dict.nodes.current3}
                        subtitle={dict.status.current}
                    />
                </div>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked1}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked2}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked3}
                        subtitle={dict.status.locked}
                    />
                </div>

                <div className='flex flex-col gap-12'>
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked4}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked5}
                        subtitle={dict.status.locked}
                    />
                    <BackgroundNode
                        status='locked'
                        title={dict.nodes.locked6}
                        subtitle={dict.status.locked}
                    />
                </div>
            </div>
        </div>
    );
}

export default function LoginPage() {
    const navigate = useNavigate();
    const setTokens = useAuthStore((state) => state.setTokens);

    const [isLoading, setIsLoading] = useState(false);
    const dict = ES_UI.auth.login;

    const handleGoogleSuccess = async (response: CredentialResponse) => {
        if (!response.credential) return;

        try {
            setIsLoading(true);

            const decoded = jwtDecode<GoogleJwtPayload>(response.credential);

            if (!decoded.email.endsWith('@unsa.edu.pe')) {
                toast.error(dict.errors.invalidDomain);
                setIsLoading(false);
                return;
            }

            const apiRes = await api.post('/accounts/auth/google/', {
                id_token: response.credential,
            });

            const tokens = apiRes.data.data;
            setTokens(tokens);

            toast.success('¡Sesión iniciada correctamente!');
            navigate(publicPaths.home);
        } catch (err: unknown) {
            console.error('Error en el login:', err);

            if (axios.isAxiosError(err)) {
                if (!err.response) {
                    toast.error(dict.errors.networkError);
                } else {
                    toast.error(dict.errors.default);
                }
            } else {
                toast.error(dict.errors.default);
            }
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className='relative flex min-h-screen items-center justify-center bg-background px-4 py-12 sm:px-6 lg:px-8 overflow-hidden'>
            <SEO title={dict.seo.title} description={dict.seo.description} />

            <BackgroundMeshWidget />

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
                                    width='100%'
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
