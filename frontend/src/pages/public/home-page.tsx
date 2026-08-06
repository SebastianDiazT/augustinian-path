import { ArrowDown, CalendarDays, CalendarPlus, Network } from 'lucide-react';

import { FeatureCard } from '@/components/marketing/feature-card';
import { HeroProductPreview } from '@/components/marketing/hero-product-preview';
import { Reveal } from '@/components/motion/reveal';
import { HeroAuthAction } from '@/features/auth/components/hero-auth-action';

export function HomePage() {
    return (
        <>
            <section
                id='home'
                className='scroll-mt-24 px-4 py-16 sm:px-6 lg:py-24'
                aria-labelledby='home-title'
            >
                <div className='mx-auto grid w-full max-w-7xl items-center gap-12 lg:grid-cols-[0.9fr_1.1fr]'>
                    <div className='animate-reveal-soft'>
                        <span className='inline-flex rounded-full border border-primary/15 bg-primary/8 px-3 py-1.5 text-xs font-extrabold uppercase tracking-[0.14em] text-primary'>
                            Planificación académica
                        </span>

                        <h1
                            id='home-title'
                            className='mt-6 max-w-2xl text-balance font-display text-4xl leading-tight font-extrabold tracking-[-0.045em] text-primary sm:text-5xl lg:text-6xl'
                        >
                            Planifica tu futuro académico con claridad
                        </h1>

                        <p className='mt-6 max-w-xl text-pretty text-base leading-8 text-muted-foreground sm:text-lg'>
                            Organiza tus cursos, explora tu malla curricular y construye
                            un horario que se adapte a tus objetivos.
                        </p>

                        <div className='mt-8 flex flex-col gap-3 sm:flex-row sm:items-start'>
                            <HeroAuthAction />

                            <a
                                href='#features'
                                className='group inline-flex min-h-12 items-center justify-center gap-2 rounded-xl border border-primary px-6 text-sm font-extrabold text-primary transition-[transform,background-color] duration-200 hover:bg-primary/8 active:translate-y-px focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'
                            >
                                Explorar funciones
                                <ArrowDown
                                    className='size-4 transition-transform duration-200 motion-safe:group-hover:translate-y-0.5'
                                    aria-hidden='true'
                                />
                            </a>
                        </div>

                        <p className='mt-5 max-w-xl text-xs leading-5 text-muted-foreground'>
                            Accede con tu cuenta institucional. Si es tu primera vez,
                            crearemos tu cuenta automáticamente.
                        </p>
                    </div>

                    <HeroProductPreview />
                </div>
            </section>

            <section
                id='features'
                className='scroll-mt-24 border-y border-border bg-surface-muted/45 px-4 py-16 sm:px-6 lg:py-24'
                aria-labelledby='features-title'
            >
                <Reveal className='mx-auto w-full max-w-7xl'>
                    <div className='mx-auto max-w-3xl text-center'>
                        <p className='text-xs font-extrabold uppercase tracking-[0.16em] text-primary'>
                            Todo en un solo lugar
                        </p>

                        <h2
                            id='features-title'
                            className='mt-4 text-balance font-display text-3xl font-extrabold tracking-[-0.035em] sm:text-4xl'
                        >
                            Diseñada para acompañar tus decisiones académicas
                        </h2>

                        <p className='mx-auto mt-4 max-w-2xl text-pretty leading-7 text-muted-foreground'>
                            Conoce tu avance, prepara distintos escenarios y organiza
                            mejor cada semestre.
                        </p>
                    </div>

                    <div className='mt-12 grid grid-cols-1 gap-6 md:grid-cols-3 lg:mt-14'>
                        <FeatureCard
                            icon={Network}
                            title='Visualiza tu malla'
                            description='Identifica cursos, prerrequisitos y el avance alcanzado dentro de tu plan de estudios.'
                        />

                        <FeatureCard
                            icon={CalendarDays}
                            title='Organiza tu horario'
                            description='Compara diferentes escenarios y detecta cruces antes de definir tu planificación.'
                        />

                        <FeatureCard
                            icon={CalendarPlus}
                            title='Exporta tu calendario'
                            description='Prepara tu horario para utilizarlo posteriormente en aplicaciones compatibles con calendarios.'
                        />
                    </div>
                </Reveal>
            </section>
        </>
    );
}
