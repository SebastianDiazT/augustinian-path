import { ArrowDown, ArrowRight, CalendarDays, Network, Sparkles, BookOpenCheck, LogIn } from 'lucide-react';
import { Link } from 'react-router-dom';
import { publicPaths, privatePaths } from '@/app/paths';
import { ES_UI } from '@/locales/es';
import { FeatureCard } from '@/components/marketing/feature-card';
import { Button } from '@/components/ui/button';
import { HeroProductPreview } from '@/components/marketing/hero-product-preview';
import { SEO } from '@/components/seo';
import { useAuthStore } from '@/store/auth-store';

const scrollToFeatures = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
};

export default function HomePage() {
    const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

    return (
        <div className='flex flex-col'>
            <SEO title={ES_UI.marketing.seo.title} description={ES_UI.marketing.seo.description} />
            <section
                id='home'
                className='scroll-mt-24 px-4 py-16 sm:px-6 lg:py-24'
                aria-labelledby='home-title'
            >
                <div className='mx-auto grid w-full max-w-7xl items-center gap-12 lg:grid-cols-[0.9fr_1.1fr]'>
                    <div className='animate-reveal-soft opacity-0'>
                        <span className='inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-3 py-1.5 text-xs font-extrabold uppercase tracking-widest text-primary dark:bg-primary/10'>
                            <Sparkles className='size-3.5 text-accent' aria-hidden='true' />
                            {ES_UI.marketing.heroBadge}
                        </span>

                        <h1
                            id='home-title'
                            className='mt-6 max-w-2xl text-balance font-display text-4xl leading-tight font-extrabold tracking-[-0.045em] text-foreground sm:text-5xl lg:text-6xl'
                        >
                            {ES_UI.marketing.heroTitle}{' '}
                            <span className='text-primary'>
                                {ES_UI.marketing.heroTitleHighlight}
                            </span>
                        </h1>

                        <p className='mt-6 max-w-xl text-pretty text-base leading-8 text-muted-foreground sm:text-lg'>
                            {ES_UI.marketing.heroSubtitle}
                        </p>

                        <div className='mt-8 flex flex-col gap-3 sm:flex-row sm:items-center'>
                            <Link to={isAuthenticated ? privatePaths.dashboard : publicPaths.login} className='w-full sm:w-auto'>
                                <Button
                                    size='lg'
                                    className='w-full h-12 rounded-xl px-6 text-sm font-extrabold shadow-md transition-transform hover:scale-[1.02] active:scale-95'
                                >
                                    {isAuthenticated
                                        ? ES_UI.marketing.heroCtaAuth
                                        : ES_UI.marketing.heroCta}
                                    {isAuthenticated ? (
                                        <ArrowRight className='ml-2 size-4' aria-hidden='true' />
                                    ) : (
                                        <LogIn className='ml-2 size-4' aria-hidden='true' />
                                    )}
                                </Button>
                            </Link>

                            <a
                                href='#features'
                                onClick={scrollToFeatures}
                                className='group inline-flex h-12 w-full sm:w-auto items-center justify-center gap-2 rounded-xl border border-border px-6 text-sm font-extrabold text-foreground transition-colors hover:bg-surface-muted focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary'
                            >
                                {ES_UI.marketing.heroSecondaryCta}
                                <ArrowDown
                                    className='size-4 transition-transform duration-200 motion-safe:group-hover:translate-y-1'
                                    aria-hidden='true'
                                />
                            </a>
                        </div>

                        <p className='mt-5 max-w-xl text-xs leading-5 text-muted-foreground'>
                            {ES_UI.marketing.heroDisclaimer}
                        </p>
                    </div>

                    <HeroProductPreview />
                </div>
            </section>

            <section
                id='features'
                className='border-y border-border bg-surface-muted/50 px-4 py-20 sm:px-6 lg:py-32'
                aria-labelledby='features-title'
            >
                <div className='mx-auto max-w-7xl'>
                    <div className='mb-16 max-w-2xl text-center sm:text-left animate-reveal-soft opacity-0'>
                        <h2
                            id='features-title'
                            className='font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl'
                        >
                            {ES_UI.marketing.featuresTitle}
                        </h2>
                        <p className='mt-4 text-lg leading-relaxed text-muted-foreground'>
                            {ES_UI.marketing.featuresSubtitle}
                        </p>
                    </div>

                    <div className='grid gap-6 sm:grid-cols-2 lg:grid-cols-3'>
                        <FeatureCard
                            icon={Network}
                            title={ES_UI.marketing.features.visualize.title}
                            description={ES_UI.marketing.features.visualize.description}
                            className='animate-reveal-soft opacity-0'
                        />
                        <FeatureCard
                            icon={CalendarDays}
                            title={ES_UI.marketing.features.schedules.title}
                            description={ES_UI.marketing.features.schedules.description}
                            className='animate-reveal-soft opacity-0'
                            style={{ animationDelay: '150ms' }}
                        />
                        <FeatureCard
                            icon={BookOpenCheck}
                            title={ES_UI.marketing.features.simulator.title}
                            description={ES_UI.marketing.features.simulator.description}
                            className='animate-reveal-soft opacity-0'
                            style={{ animationDelay: '300ms' }}
                        />
                    </div>
                </div>
            </section>

            <section className='relative isolate px-4 py-20 sm:px-6 lg:py-32'>
                <div
                    className='mx-auto max-w-4xl overflow-hidden rounded-4xl border border-border bg-surface px-6 py-16 text-center shadow-card sm:px-16 animate-reveal-soft opacity-0'
                    style={{ animationDelay: '400ms' }}
                >
                    <h2 className='font-display text-3xl font-extrabold tracking-tight text-foreground sm:text-4xl'>
                        {ES_UI.marketing.bottomCta.title}
                    </h2>
                    <p className='mx-auto mt-6 max-w-xl text-lg leading-relaxed text-muted-foreground'>
                        {ES_UI.marketing.bottomCta.description}
                    </p>
                    <div className='mt-10 flex justify-center'>
                        <Link to={isAuthenticated ? privatePaths.dashboard : publicPaths.login}>
                            <Button
                                size='lg'
                                className='h-14 rounded-2xl px-10 text-base font-bold shadow-lg transition-transform hover:scale-[1.03] active:scale-95'
                            >
                                {isAuthenticated
                                    ? ES_UI.marketing.bottomCta.buttonAuth
                                    : ES_UI.marketing.bottomCta.button}
                                {isAuthenticated ? (
                                    <ArrowRight
                                        className='ml-2 size-4 shrink-0 transition-transform hover:translate-x-1'
                                        aria-hidden='true'
                                    />
                                ) : (
                                    <LogIn
                                        className='ml-2 size-4 shrink-0 transition-transform hover:translate-x-1'
                                        aria-hidden='true'
                                    />
                                )}
                            </Button>
                        </Link>
                    </div>
                </div>
            </section>
        </div>
    );
}
